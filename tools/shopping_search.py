from langchain_core.tools import tool
import requests
@tool
def shopping_search(query: str) -> str:
    """
    Search products online.

    Input:
    - A query string (str), e.g. "buy iPhone 15".

    Output:
    - Product search results with details and links.

    When to use:
    - When user asks to "find", "compare", or "buy" a product online.

    """
    try:
        ddg_url = f"https://duckduckgo.com/html/?q={query}+buy"
        response = requests.get(ddg_url, headers={"User-Agent": "Mozilla/5.0"})
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        results = [a["href"] for a in soup.select(".result__a")[:5]]
        return "\n".join(results) if results else "No shopping results found."
    except Exception as e:
        return f"Error in shopping search: {str(e)}"