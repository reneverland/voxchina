try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None
from loguru import logger

class WebSearchService:
    def __init__(self):
        pass

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Searches the web using DuckDuckGo.
        """
        if not DDGS:
            logger.warning("duckduckgo_search not installed. Returning mock results.")
            return self._mock_search(query)

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return results
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return self._mock_search(query)

    def _mock_search(self, query: str) -> list[dict]:
        # Fallback if no internet or lib missing
        return [
            {
                "title": f"Latest news on {query}",
                "body": f"This is a simulated search result for {query}. Real-time data requires internet access and the duckduckgo-search library.",
                "href": "http://example.com"
            }
        ]

web_search_service = WebSearchService()







