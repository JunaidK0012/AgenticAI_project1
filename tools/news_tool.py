import requests, os
from langchain_core.tools import Tool,tool

@tool
def news_search(query: str) -> str:
    """
    Search latest news headlines by topic.
    Requires NEWS_API_KEY in .env
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "❌ Missing NEWS_API_KEY in environment."
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={api_key}"
    r = requests.get(url)
    if r.status_code != 200:
        return f"❌ Error fetching news: {r.text}"
    articles = r.json().get("articles", [])[:5]
    if not articles:
        return "📭 No news found."
    return "\n".join([f"📰 {a['title']} ({a['url']})" for a in articles])
