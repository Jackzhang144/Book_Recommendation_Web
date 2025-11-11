"""Simple smoke tests for the Flask API."""

import json
import time

import requests

BASE_URL = "http://localhost:8000/api"


def pretty_print(title, response):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(response.text)


def main():
    time.sleep(1)
    endpoints = [
        ("Health", f"{BASE_URL}/health", {}),
        ("Search", f"{BASE_URL}/books/search", {"q": "harry potter", "limit": 3}),
        ("Recommendations by title", f"{BASE_URL}/recommendations/by-title", {"q": "Classical Mythology"}),
    ]

    for title, url, params in endpoints:
        resp = requests.get(url, params=params or None, timeout=10)
        pretty_print(title, resp)


if __name__ == "__main__":
    main()

