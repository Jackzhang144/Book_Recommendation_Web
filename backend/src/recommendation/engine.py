"""Coordinator that wires repositories with algorithm implementations."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .algorithms.base import AlgorithmInfo, BaseRecommender, RecommendationError
from .algorithms.content_based import DINContentRecommender
from .algorithms.lightfm_cf import LightFMCollaborativeRecommender
from .algorithms.lightgbm_pairwise import LightGBMPairwiseRecommender


class RecommendationEngine:
    """Registers all algorithms and routes requests with graceful fallbacks."""

    def __init__(self, book_repo):
        self.book_repo = book_repo
        self.algorithms: Dict[str, BaseRecommender] = {}
        self.aliases = {
            "user_cf": "cf_mf",
            "item_cf": "cf_mf",
            "deepfm": "din_content",
        }
        self._initialize_algorithms()

    def _initialize_algorithms(self) -> None:
        for cls in (
            LightGBMPairwiseRecommender,
            DINContentRecommender,
            LightFMCollaborativeRecommender,
        ):
            instance = cls(self.book_repo)
            self.algorithms[instance.info.id] = instance

    def list_algorithms(self) -> List[Dict]:
        base_list = [
            {"id": algo.info.id, "name": algo.info.name, "description": algo.info.description}
            for algo in self.algorithms.values()
        ]
        alias_descriptions = {
            "user_cf": "User-based CF (alias of LightFM)",
            "item_cf": "Item-based CF (alias of LightFM)",
            "deepfm": "DIN content model (alias of DIN)",
        }
        for alias, target in self.aliases.items():
            base_list.append(
                {
                    "id": alias,
                    "name": alias_descriptions.get(alias, alias),
                    "description": f"Alias of {self.algorithms[target].info.name}",
                }
            )
        return base_list

    def recommend(
        self,
        isbn: str,
        k: int,
        algorithm_id: Optional[str] = None,
    ) -> Tuple[List[Dict], AlgorithmInfo]:
        """Try requested algorithm or fall back to defaults."""
        ordered_algorithms: List[BaseRecommender]
        if algorithm_id:
            resolved_id = self.aliases.get(algorithm_id, algorithm_id)
            algo = self.algorithms.get(resolved_id)
            if not algo:
                raise RecommendationError(f"Unsupported algorithm: {algorithm_id}")
            ordered_algorithms = [algo]
        else:
            priority = ["lightgbm", "din_content", "cf_mf"]
            ordered_algorithms = [self.algorithms[name] for name in priority if name in self.algorithms]

        last_error: Optional[Exception] = None
        for algo in ordered_algorithms:
            try:
                return algo.recommend(isbn, k), algo.info
            except RecommendationError as exc:
                last_error = exc
                continue
        raise RecommendationError(str(last_error) if last_error else "No algorithms configured")
