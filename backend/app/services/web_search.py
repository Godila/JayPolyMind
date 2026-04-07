"""
Web Search Abstraction Layer
Provides unified interface for web search via SearXNG (primary) or DuckDuckGo (fallback).
All options are free and open-source. No paid API keys required.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

import requests

from ..config import Config

logger = logging.getLogger('jaypolymind.web_search')


@dataclass
class SearchResult:
    """Single web search result."""
    title: str
    url: str
    content: str
    score: float = 0.0
    published_date: Optional[str] = None


class WebSearchClient(ABC):
    """Abstract web search interface."""

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        ...


class SearXNGSearchClient(WebSearchClient):
    """
    SearXNG -- self-hosted metasearch engine.
    Aggregates results from 70+ search engines (Google, Bing, DuckDuckGo, Wikipedia, etc.).
    Deployed as a Docker container alongside the main stack.
    JSON API: GET /search?q=query&format=json
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            resp = requests.get(
                f"{self.base_url}/search",
                params={
                    "q": query,
                    "format": "json",
                    "categories": "general",
                    "language": "auto",
                    "safesearch": 0,
                },
                headers={"Accept": "application/json"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("results", [])[:max_results]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.5),
                    published_date=item.get("publishedDate"),
                ))
            return results
        except Exception as e:
            logger.error(f"SearXNG search failed for '{query}': {e}")
            return []


class DuckDuckGoSearchClient(WebSearchClient):
    """DuckDuckGo fallback -- free, no API key needed."""

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for item in ddgs.text(query, max_results=max_results):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("href", ""),
                        content=item.get("body", ""),
                        score=0.5,
                    ))
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for '{query}': {e}")
            return []


def create_search_client() -> WebSearchClient:
    """Factory: SearXNG if URL configured, otherwise DuckDuckGo fallback."""
    searxng_url = Config.SEARXNG_URL
    if searxng_url:
        logger.info(f"Using SearXNG search client at {searxng_url}")
        return SearXNGSearchClient(base_url=searxng_url)
    logger.info("SEARXNG_URL not set, using DuckDuckGo fallback")
    return DuckDuckGoSearchClient()
