"""DIN sequential recommender built on user behavior sequences."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from ...config import (
    DIN_BATCH_SIZE,
    DIN_CANDIDATE_POOL_SIZE,
    DIN_EPOCHS,
    DIN_EMBED_DIM,
    DIN_ATTENTION_HIDDEN_UNITS,
    DIN_LEARNING_RATE,
    DIN_MAX_HISTORIES_PER_ITEM,
    DIN_MAX_HISTORY_LENGTH,
    DIN_MAX_TRAINING_SAMPLES,
    DIN_MAX_USERS,
    DIN_MIN_HISTORY_LENGTH,
    DIN_MIN_POSITIVE_RATING,
    DIN_MLP_HIDDEN_UNITS,
    DIN_NEGATIVE_SAMPLES,
    DIN_RANDOM_STATE,
    DIN_SCORE_BATCH_SIZE,
)
from ...data_pipeline import get_ratings, get_users
from .base import AlgorithmInfo, BaseRecommender, RecommendationError


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


@dataclass
class ContextBatch:
    histories: torch.Tensor
    lengths: torch.Tensor
    user_features: torch.Tensor


class DinTrainingSample:
    __slots__ = ("history", "target", "label", "user_feature")

    def __init__(self, history: List[int], target: int, label: float, user_feature: float):
        self.history = history
        self.target = target
        self.label = label
        self.user_feature = user_feature


class DinDataset(Dataset):
    def __init__(self, samples: Sequence[DinTrainingSample], max_history_len: int):
        self.samples = samples
        self.max_history_len = max_history_len

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict:
        sample = self.samples[idx]
        history = sample.history
        padded = np.zeros(self.max_history_len, dtype=np.int64)
        length = min(len(history), self.max_history_len)
        if length > 0:
            padded[-length:] = history[-length:]
        return {
            "history": padded,
            "length": length,
            "target": sample.target,
            "label": sample.label,
            "user_feature": sample.user_feature,
        }

    @staticmethod
    def collate_fn(batch: List[Dict]) -> Dict[str, torch.Tensor]:
        histories = torch.tensor([row["history"] for row in batch], dtype=torch.long)
        lengths = torch.tensor([row["length"] for row in batch], dtype=torch.long)
        targets = torch.tensor([row["target"] for row in batch], dtype=torch.long)
        labels = torch.tensor([row["label"] for row in batch], dtype=torch.float32)
        user_features = torch.tensor([[row["user_feature"]] for row in batch], dtype=torch.float32)
        return {
            "histories": histories,
            "lengths": lengths,
            "targets": targets,
            "labels": labels,
            "user_features": user_features,
        }


class DINModel(nn.Module):
    def __init__(self, num_items: int, embed_dim: int, att_hidden_units: Tuple[int, ...], mlp_hidden_units: Tuple[int, ...]):
        super().__init__()
        self.item_embedding = nn.Embedding(num_items + 1, embed_dim, padding_idx=0)

        att_layers: List[nn.Module] = []
        input_dim = embed_dim * 4
        for units in att_hidden_units:
            att_layers.append(nn.Linear(input_dim, units))
            att_layers.append(nn.ReLU())
            att_layers.append(nn.Dropout(0.1))
            input_dim = units
        att_layers.append(nn.Linear(input_dim, 1))
        self.attention_mlp = nn.Sequential(*att_layers)

        mlp_layers: List[nn.Module] = []
        input_dim = embed_dim * 2 + 1
        for units in mlp_hidden_units:
            mlp_layers.append(nn.Linear(input_dim, units))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(0.1))
            input_dim = units
        mlp_layers.append(nn.Linear(input_dim, 1))
        self.scorer = nn.Sequential(*mlp_layers)

    def forward(self, targets: torch.Tensor, histories: torch.Tensor, lengths: torch.Tensor, user_features: torch.Tensor) -> torch.Tensor:
        target_emb = self.item_embedding(targets)
        hist_emb = self.item_embedding(histories)
        seq_len = histories.size(1)

        query = target_emb.unsqueeze(1).expand(-1, seq_len, -1)
        att_input = torch.cat([query, hist_emb, query - hist_emb, query * hist_emb], dim=-1)
        att_scores = self.attention_mlp(att_input).squeeze(-1)

        device = histories.device
        position_ids = torch.arange(seq_len, device=device).unsqueeze(0)
        mask = position_ids >= lengths.unsqueeze(1)
        att_scores = att_scores.masked_fill(mask, float("-inf"))
        att_weights = torch.softmax(att_scores, dim=-1)
        att_weights = torch.where(torch.isfinite(att_weights), att_weights, torch.zeros_like(att_weights))
        user_interest = torch.sum(att_weights.unsqueeze(-1) * hist_emb, dim=1)

        final_input = torch.cat([user_interest, target_emb, user_features], dim=-1)
        logits = self.scorer(final_input).squeeze(-1)
        return logits


class DINContentRecommender(BaseRecommender):
    """Sequential DIN recommender trained from user histories."""

    info = AlgorithmInfo(
        id="din_content",
        name="DIN Sequential Recommendation",
        description="User-behavior DIN model over reading histories",
    )

    def __init__(self, book_repo):
        super().__init__(book_repo)
        _seed_everything(DIN_RANDOM_STATE)
        self.device = torch.device("cpu")
        self.df = book_repo.get_dataframe()
        self.isbn_to_index = {isbn: idx + 1 for idx, isbn in enumerate(self.df["ISBN"].tolist())}
        self.index_to_isbn = {idx: isbn for isbn, idx in self.isbn_to_index.items()}

        self.user_age_map = self._build_user_age_map()
        samples, book_contexts, candidate_isbns = self._prepare_training_samples()
        if not samples:
            raise RuntimeError("DIN recommender could not create training samples")

        self.candidate_isbns = candidate_isbns
        self.model = self._train_model(samples)
        self.context_store = self._build_context_store(book_contexts)
        if not self.context_store:
            raise RuntimeError("DIN recommender failed to capture any user contexts")

    def _build_user_age_map(self) -> Dict[int, float]:
        users = get_users()
        users["Age"] = users["Age"].clip(lower=5, upper=90)
        median_age = users["Age"].median()
        users["Age"] = users["Age"].fillna(median_age)
        min_age, max_age = users["Age"].min(), users["Age"].max()
        denom = max(max_age - min_age, 1)
        users["age_norm"] = (users["Age"] - min_age) / denom
        return users.set_index("User-ID")["age_norm"].to_dict()

    def _prepare_training_samples(self) -> Tuple[List[DinTrainingSample], Dict[str, List[Tuple[List[int], float]]], List[str]]:
        ratings = get_ratings(filtered=True)
        ratings = ratings[ratings["Book-Rating"] >= DIN_MIN_POSITIVE_RATING]
        if ratings.empty:
            raise RuntimeError("DIN recommender requires positive ratings")

        ratings = ratings[ratings["ISBN"].isin(self.isbn_to_index.keys())]
        if ratings.empty:
            raise RuntimeError("No overlapping ISBNs between ratings and catalog for DIN")

        ratings = ratings.reset_index().rename(columns={"index": "_row_order"})
        ratings = ratings.sort_values(["User-ID", "_row_order"])

        user_lengths = ratings.groupby("User-ID")["ISBN"].count()
        eligible_users = user_lengths[user_lengths >= DIN_MIN_HISTORY_LENGTH + 1]
        if eligible_users.empty:
            raise RuntimeError("Not enough users with sufficient histories for DIN")
        selected_users = eligible_users.sort_values(ascending=False).head(DIN_MAX_USERS).index.tolist()
        filtered = ratings[ratings["User-ID"].isin(selected_users)]

        book_popularity = filtered["ISBN"].value_counts()
        candidate_isbns = [isbn for isbn in book_popularity.index.tolist() if isbn in self.isbn_to_index][:DIN_CANDIDATE_POOL_SIZE]
        if not candidate_isbns:
            raise RuntimeError("DIN candidate pool is empty")

        samples: List[DinTrainingSample] = []
        book_contexts: Dict[str, List[Tuple[List[int], float]]] = defaultdict(list)
        rng = random.Random(DIN_RANDOM_STATE)
        max_samples = DIN_MAX_TRAINING_SAMPLES

        for user_id, group in filtered.groupby("User-ID"):
            isbn_seq = [isbn for isbn in group["ISBN"].tolist() if isbn in self.isbn_to_index]
            if len(isbn_seq) <= DIN_MIN_HISTORY_LENGTH:
                continue
            age_norm = self.user_age_map.get(user_id, 0.5)
            positive_set = set(isbn_seq)

            for idx in range(1, len(isbn_seq)):
                history = isbn_seq[max(0, idx - DIN_MAX_HISTORY_LENGTH) : idx]
                if len(history) < DIN_MIN_HISTORY_LENGTH:
                    continue
                target_isbn = isbn_seq[idx]
                history_indices = [self.isbn_to_index[h] for h in history]
                target_idx = self.isbn_to_index[target_isbn]

                samples.append(DinTrainingSample(history_indices, target_idx, 1.0, age_norm))
                if len(samples) >= max_samples:
                    break

                if len(book_contexts[target_isbn]) < DIN_MAX_HISTORIES_PER_ITEM:
                    book_contexts[target_isbn].append((history_indices, age_norm))

                negatives_added = 0
                attempts = 0
                while negatives_added < DIN_NEGATIVE_SAMPLES and attempts < DIN_NEGATIVE_SAMPLES * 4:
                    negative_isbn = rng.choice(candidate_isbns)
                    attempts += 1
                    if negative_isbn in positive_set:
                        continue
                    negative_idx = self.isbn_to_index[negative_isbn]
                    samples.append(DinTrainingSample(history_indices, negative_idx, 0.0, age_norm))
                    negatives_added += 1
                    if len(samples) >= max_samples:
                        break
                if len(samples) >= max_samples:
                    break
            if len(samples) >= max_samples:
                break

        return samples, book_contexts, candidate_isbns

    def _train_model(self, samples: List[DinTrainingSample]) -> DINModel:
        dataset = DinDataset(samples, max_history_len=DIN_MAX_HISTORY_LENGTH)
        loader = DataLoader(dataset, batch_size=DIN_BATCH_SIZE, shuffle=True, collate_fn=DinDataset.collate_fn)
        num_items = len(self.isbn_to_index)
        model = DINModel(num_items, DIN_EMBED_DIM, DIN_ATTENTION_HIDDEN_UNITS, DIN_MLP_HIDDEN_UNITS)
        model.to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=DIN_LEARNING_RATE)
        criterion = nn.BCEWithLogitsLoss()

        model.train()
        for _ in range(DIN_EPOCHS):
            for batch in loader:
                histories = batch["histories"].to(self.device)
                lengths = batch["lengths"].to(self.device)
                targets = batch["targets"].to(self.device)
                labels = batch["labels"].to(self.device)
                user_features = batch["user_features"].to(self.device)

                optimizer.zero_grad()
                logits = model(targets, histories, lengths, user_features)
                loss = criterion(logits, labels)
                loss.backward()
                optimizer.step()
        model.eval()
        return model

    def _build_context_store(self, book_contexts: Dict[str, List[Tuple[List[int], float]]]) -> Dict[str, ContextBatch]:
        store: Dict[str, ContextBatch] = {}
        for isbn, contexts in book_contexts.items():
            if not contexts:
                continue
            histories = []
            lengths = []
            user_feats = []
            for history_indices, user_feature in contexts:
                padded = np.zeros(DIN_MAX_HISTORY_LENGTH, dtype=np.int64)
                length = min(len(history_indices), DIN_MAX_HISTORY_LENGTH)
                padded[-length:] = history_indices[-length:]
                histories.append(padded)
                lengths.append(length)
                user_feats.append([user_feature])
            histories_tensor = torch.tensor(histories, dtype=torch.long, device=self.device)
            lengths_tensor = torch.tensor(lengths, dtype=torch.long, device=self.device)
            user_feats_tensor = torch.tensor(user_feats, dtype=torch.float32, device=self.device)
            store[isbn] = ContextBatch(histories_tensor, lengths_tensor, user_feats_tensor)
        return store

    def recommend(self, isbn: str, k: int) -> List[Dict]:
        if isbn not in self.context_store:
            raise RecommendationError("DIN model has no behavioral context for this book")

        target_index = self.isbn_to_index.get(isbn)
        if not target_index:
            raise RecommendationError("Book not found in DIN index")

        contexts = self.context_store[isbn]
        candidate_indices = [self.isbn_to_index[cand] for cand in self.candidate_isbns if cand != isbn]
        if not candidate_indices:
            raise RecommendationError("DIN candidate pool is empty after filtering")

        scored = self._score_candidates(contexts, candidate_indices)
        if not scored:
            raise RecommendationError("DIN scoring produced no candidates")

        scored.sort(key=lambda item: item[1], reverse=True)
        results: List[Dict] = []
        for idx, score in scored:
            candidate_isbn = self.index_to_isbn.get(idx)
            if not candidate_isbn:
                continue
            payload = self._format_result(candidate_isbn, score)
            if payload:
                results.append(payload)
            if len(results) >= k:
                break
        if not results:
            raise RecommendationError("DIN recommender returned empty results")
        return results

    def _score_candidates(self, contexts: ContextBatch, candidate_indices: List[int]) -> List[Tuple[int, float]]:
        histories = contexts.histories
        lengths = contexts.lengths
        user_features = contexts.user_features
        ctx_count = histories.size(0)
        seq_len = histories.size(1)
        user_feat_dim = user_features.size(-1)

        scored: List[Tuple[int, float]] = []
        with torch.no_grad():
            for start in range(0, len(candidate_indices), DIN_SCORE_BATCH_SIZE):
                batch_ids = candidate_indices[start : start + DIN_SCORE_BATCH_SIZE]
                batch_size = len(batch_ids)
                target_tensor = torch.tensor(batch_ids, dtype=torch.long, device=self.device).unsqueeze(1)
                target_tensor = target_tensor.repeat(1, ctx_count).view(-1)

                histories_batch = histories.unsqueeze(0).repeat(batch_size, 1, 1).view(-1, seq_len)
                lengths_batch = lengths.unsqueeze(0).repeat(batch_size, 1).view(-1)
                user_feats_batch = user_features.unsqueeze(0).repeat(batch_size, 1, 1).view(-1, user_feat_dim)

                logits = self.model(target_tensor, histories_batch, lengths_batch, user_feats_batch)
                probs = torch.sigmoid(logits).view(batch_size, ctx_count).mean(dim=1)
                scored.extend(list(zip(batch_ids, probs.cpu().tolist())))
        return scored
