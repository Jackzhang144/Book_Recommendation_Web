"""Flask application exposing the REST API consumed by the Vue frontend."""

from __future__ import annotations

from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from ..book_repository import BookRepository
from ..config import DEFAULT_SEARCH_LIMIT, DEFAULT_TOP_K
from ..data_pipeline import get_clean_books
from ..recommendation.engine import RecommendationEngine
from ..recommendation.algorithms.base import RecommendationError

app = Flask(__name__)
CORS(app)

books_df = get_clean_books()
BOOK_REPO = BookRepository(books_df)
ENGINE = RecommendationEngine(BOOK_REPO)


def create_response(code=0, message="ok", data=None, status=200):
    payload = {"code": code, "message": message, "data": data}
    return jsonify(payload), status


def parse_positive_int(value: str, fallback: int) -> int:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else fallback
    except (TypeError, ValueError):
        return fallback


@app.route("/api/health", methods=["GET"])
def health_check():
    return create_response(
        data={
            "status": "healthy",
            "total_books": len(BOOK_REPO.by_id),
            "algorithms": [algo["id"] for algo in ENGINE.list_algorithms()],
        }
    )


@app.route("/api/books/search", methods=["GET"])
def search_books():
    query = request.args.get("q", "").strip()
    limit = parse_positive_int(request.args.get("limit"), DEFAULT_SEARCH_LIMIT)
    if not query:
        return create_response(1, "参数缺失：搜索关键词不能为空", status=400)
    results = BOOK_REPO.search(query, limit)
    if not results:
        return create_response(2, "没有搜索到任何图书", {"books": []})
    return create_response(data={"books": results})


@app.route("/api/books/<book_id>", methods=["GET"])
def get_book_detail(book_id):
    book = BOOK_REPO.get_by_id(book_id)
    if not book:
        return create_response(404, "没有找到该图书", status=404)
    return create_response(data={"book": book})


def _recommend_by_isbn(isbn: str, k: int, algorithm: Optional[str] = None):
    recommendations, algo_info = ENGINE.recommend(isbn, k, algorithm_id=algorithm)
    return recommendations, algo_info


@app.route("/api/recommendations/by-title", methods=["GET"])
def recommend_by_title():
    query = request.args.get("q", "").strip()
    k = parse_positive_int(request.args.get("k"), DEFAULT_TOP_K)
    if not query:
        return create_response(1, "参数缺失：书名不能为空", status=400)

    exact_book = BOOK_REPO.find_exact_by_title(query)
    if not exact_book:
        suggestions = BOOK_REPO.suggest_titles(query, limit=5)
        if suggestions:
            return create_response(3, "未找到精确匹配的书籍，请尝试以下书名:", {"similar_titles": suggestions})
        return create_response(2, "没有找到相关图书", {"recommendations": []})

    try:
        recommendations, algo_info = _recommend_by_isbn(exact_book["isbn"], k)
    except RecommendationError as exc:
        return create_response(2, f"无法生成推荐：{exc}", {"recommendations": []})

    return create_response(
        data={
            "query_title": exact_book["title"],
            "query_book": exact_book,
            "recommendations": recommendations,
            "algorithm": {"id": algo_info.id, "name": algo_info.name},
        }
    )


@app.route("/api/recommendations/by-book", methods=["GET"])
def recommend_by_book():
    book_id = request.args.get("book_id", "").strip()
    k = parse_positive_int(request.args.get("k"), DEFAULT_TOP_K)
    if not book_id:
        return create_response(1, "参数缺失：book_id 不能为空", status=400)
    book = BOOK_REPO.get_by_id(book_id)
    if not book:
        return create_response(404, "没有找到该图书", status=404)
    try:
        recommendations, algo_info = _recommend_by_isbn(book["isbn"], k)
    except RecommendationError as exc:
        return create_response(2, f"无法生成推荐：{exc}", {"recommendations": []})
    return create_response(
        data={
            "query_book": book,
            "recommendations": recommendations,
            "algorithm": {"id": algo_info.id, "name": algo_info.name},
        }
    )


@app.route("/api/recommendations/by-book-and-algorithm", methods=["GET"])
def recommend_by_book_and_algorithm():
    book_id = request.args.get("book_id", "").strip()
    algorithm = request.args.get("algorithm", "lightgbm").strip()
    k = parse_positive_int(request.args.get("k"), DEFAULT_TOP_K)

    if not book_id:
        return create_response(1, "参数缺失：book_id 不能为空", status=400)
    book = BOOK_REPO.get_by_id(book_id)
    if not book:
        return create_response(404, "没有找到该图书", status=404)
    try:
        recommendations, algo_info = _recommend_by_isbn(book["isbn"], k, algorithm=algorithm or None)
    except RecommendationError as exc:
        return create_response(2, f"无法生成推荐：{exc}", {"recommendations": []})
    return create_response(
        data={
            "algorithm": {"id": algo_info.id, "name": algo_info.name},
            "query_book": book,
            "recommendations": recommendations,
        }
    )


@app.route("/api/system/algorithms", methods=["GET"])
def list_algorithms():
    return create_response(data={"algorithms": ENGINE.list_algorithms()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
