from __future__ import annotations

from typing import Any

from tavily import TavilyClient

from backend import config

_client: TavilyClient | None = None


def get_client() -> TavilyClient:
    global _client
    if _client is None:
        if not config.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is required")
        _client = TavilyClient(api_key=config.TAVILY_API_KEY)
    return _client


def search(query: str, mode: str, max_results: int = 5) -> list[dict[str, Any]]:
    domains = config.VENUE_DOMAINS if mode == "venue" else config.HOME_DOMAINS
    client = get_client()
    response = client.search(
        query=query,
        max_results=max_results,
        include_domains=domains,
    )
    return response.get("results", [])


def extract(urls: list[str]) -> list[dict[str, Any]]:
    if not urls:
        return []
    client = get_client()
    response = client.extract(urls=urls[:5])
    return response.get("results", [])
