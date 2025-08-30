from .arxiv_tool import arxiv_search
from .file_tools import read_tool,write_tool,list_tool
from .human_in_the_loop import add_human_in_the_loop
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from .youtube_tool import youtube_transcript_tool
from langchain_core.tools import Tool,tool
from langchain_experimental.utilities import PythonREPL
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import YouTubeSearchTool,WikipediaQueryRun

load_dotenv()



import sqlite3
from datetime import datetime
from langchain_core.tools import tool

cal_conn = sqlite3.connect("calendar.db", check_same_thread=False)
cal_conn.execute("CREATE TABLE IF NOT EXISTS events (title TEXT, date TEXT)")

@tool
def add_event(title: str, date: str) -> str:
    """
    Add an event to the calendar.

    Input:
    - title (str): Name or description of the event.
    - date (str): Event date in format YYYY-MM-DD.

    Output:
    - Confirmation message with event title and date.

    Notes for LLM:
    - Use when the user wants to schedule, save, or add an event.
    - Always ensure the date follows YYYY-MM-DD format.
    """
    with cal_conn:
        cal_conn.execute("INSERT INTO events VALUES (?, ?)", (title, date))
    return f"Added event '{title}' on {date}"

@tool
def list_events() -> str:
    """
    List all calendar events currently stored.

    Input:
    - None.

    Output:
    - A formatted string of all events sorted by date: "Title on YYYY-MM-DD".
    - If no events exist, returns an empty string.

    Notes for LLM:
    - Use when the user asks to view, check, or show their calendar or events.
    """
    cur = cal_conn.execute("SELECT title, date FROM events ORDER BY date")
    return "\n".join([f"{row[0]} on {row[1]}" for row in cur.fetchall()])


from langchain_community.tools import DuckDuckGoSearchRun

duck_search = DuckDuckGoSearchRun()
duck_search.description = """
Perform a DuckDuckGo web search.

Input:
- A search query (str).

Output:
- The top web search results as text snippets.

Notes for LLM:
- Use for real-time or current information that might not be in training data.
- Prefer this when the user asks for "latest", "today", or "current" news/events.
"""



#web search
tavily_search = TavilySearch()
tavily_search.description = """
Perform a Tavily web search.

Input:
- A search query (str).

Output:
- The top search results, optimized for factual and up-to-date information.

Notes for LLM:
- Use when the user asks for current events, news, or updates beyond your knowledge cutoff.
- Prefer this tool for reliable real-time answers.
"""

python_repl = PythonREPL()
# You can create the tool to pass to an agent
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)

#wikipedia
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(load_all_available_meta=True))
wikipedia_tool.description = """
Query Wikipedia for factual information.

Input:
- A search query (str).

Output:
- A summary of the most relevant Wikipedia article(s).

Notes for LLM:
- Use for general knowledge, history, definitions, and factual background information.
- Do not hallucinate content; rely on the returned Wikipedia summary.
"""

#Youtube
youtube_search_tool = YouTubeSearchTool()
youtube_search_tool.description = """
Search YouTube for videos.

Input:
- A search query (str).

Output:
- Metadata about matching YouTube videos (title, URL, etc.).

Notes for LLM:
- Use this when the user asks for a video on a topic or requests to "find on YouTube".
- To summarize or analyze a specific video, first search with this tool, then pass the URL to youtube_transcript_tool.
"""


#final tool list 
tools = [
    arxiv_search,
    read_tool,
    add_human_in_the_loop(write_tool),
    list_tool,
    duck_search,
    tavily_search,
    wikipedia_tool,
    youtube_search_tool,
    youtube_transcript_tool,
    repl_tool,
    add_event,
    list_events
    
]