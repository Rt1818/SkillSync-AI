import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from ..config import settings


# ── Tool 1: Tavily Web Search ──────────────────────────────────────────────
def get_search_tool() -> TavilySearchResults:
    """
    Returns a Tavily search tool configured for the agent.
    Tavily is purpose-built for LangChain agents and returns clean, relevant results.
    """
    import os
    os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
    return TavilySearchResults(
        max_results=5,
        name="web_search",
        description=(
            "Search the web for any information. Use this to find:\n"
            "- Learning resources, tutorials, YouTube videos for a skill\n"
            "- Company interview processes, rounds, and glassdoor reviews\n"
            "- LeetCode/HackerRank practice problems\n"
            "- Documentation and official guides\n"
            "Input should be a clear search query string."
        ),
    )


# ── Tool 2: URL Scraper ────────────────────────────────────────────────────
@tool
async def scrape_url(url: str) -> str:
    """
    Scrape and extract clean text content from any URL.
    Use this to read the full content of a job posting, article, or documentation page.
    Input: a valid URL string.
    """
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove scripts/styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Limit to 4000 chars to stay within context limits
        return text[:4000] if len(text) > 4000 else text

    except Exception as e:
        return f"Error scraping URL: {str(e)}"
