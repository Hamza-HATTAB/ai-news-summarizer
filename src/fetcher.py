import os
import logging
from typing import List, Dict, Any
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class NewsFetcher:
    """
    Handles robust news retrieval from Tavily Search API with timeframe mapping
    and fallback mock generation for testing environments.
    """
    TIMEFRAME_MAP = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
    DAYS_MAP = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 365}

    def __init__(self, tavily_api_key: str = None):
        key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.client = TavilyClient(api_key=key) if key else None

    def fetch(self, frequency: str = "daily", query: str = "Top Artificial Intelligence (AI) technology news") -> List[Dict[str, Any]]:
        """
        Fetch news articles matching query and timeframe.
        """
        freq_key = frequency.lower()
        if freq_key not in self.TIMEFRAME_MAP:
            freq_key = 'daily'

        if self.client:
            try:
                response = self.client.search(
                    query=query,
                    topic="news",
                    time_range=self.TIMEFRAME_MAP[freq_key],
                    days=self.DAYS_MAP[freq_key],
                    max_results=15,
                    include_answer="advanced"
                )
                results = response.get('results', [])
                logger.info(f"Retrieved {len(results)} news articles from Tavily API for timeframe '{freq_key}'.")
                return results
            except Exception as e:
                logger.warning(f"Tavily API search failed: {e}. Falling back to offline mock news.")

        # Offline Mock Fallback
        return [
            {
                "title": "OpenAI Unveils Advanced Reasoning Model Innovations",
                "content": "New architectural improvements enable faster reasoning, tool calling, and multi-modal alignment for production workloads.",
                "url": "https://techcrunch.com/ai-news-update",
                "published_date": "2026-08-30"
            },
            {
                "title": "Open-Source AI Breakthroughs Accelerate Edge Deployment",
                "content": "Quantization techniques and sub-billion parameter models allow high-throughput inference on consumer hardware.",
                "url": "https://venturebeat.com/ai-edge-inference",
                "published_date": "2026-08-29"
            }
        ]
