from .arxiv_tool import arxiv_search
from .file_tools import read_tool,write_tool,list_tool
from .human_in_the_loop import add_human_in_the_loop
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_community.tools import DuckDuckGoSearchRun
from .youtube_tool import youtube_transcript_tool
from .pdf_tool import generate_pdf
from .ticket_tool import create_ticket,update_ticket,list_tickets,get_ticket_details
from .news_tool import news_search
from .shopping_search import shopping_search
from langchain_core.tools import Tool,tool
from pydantic import BaseModel
from langchain_experimental.utilities import PythonREPL
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import YouTubeSearchTool,WikipediaQueryRun
from src.memory.db_connection import get_calendar_connection,get_tickets_connection

load_dotenv()

cal_conn = get_calendar_connection()
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
    - Use When user requests to add/schedule an event or reminder.
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


#web search(ddgs)
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



#web search(tavily)
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

@tool
def read_webpage(url: str) -> str:
    """
    Read and extract the main text content from a given webpage URL.

    Input:
    - url (str): The webpage link to read.

    Output:
    - The extracted textual content of the webpage (plain text)

    """
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs[0].page_content[:4000]
    except Exception as e:
        return f"Error reading webpage: {str(e)}"


#Python shell
python_repl = PythonREPL()

class PythonREPLInput(BaseModel):
    code: str

repl_tool = Tool(
    name="python_repl",
    description="""
    Execute Python code in a safe Python shell.

    Input:
    - code (str): Python code as a string. Example: "print(2+2)" or "import math; math.sqrt(16)".

    Output:
    - The result or output of the executed code.

    Priority Rules:
    - Use this ONLY when the user explicitly asks to run Python code, perform calculations, test scripts, or manipulate data.
    - Do NOT use this for general knowledge, search, or text processing; other tools are preferred for those tasks.
    - Always validate input to ensure it is safe and syntactically correct.
    """,
    args_schema=PythonREPLInput,
    func=lambda code: python_repl.run(code)  # map `code` -> REPL
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


from langchain_core.runnables import RunnableConfig
from langgraph.config import get_store

@tool
def get_user_info(config: RunnableConfig) -> str:
    """
    Retrieve stored user information.

    Input:
    - config (RunnableConfig): contains user_id for lookup.

    Output:
    - A string representation of stored user data.

    When to use:
    - When you need to recall previously saved user details (name, preferences, etc.).
    """
    store = get_store()
    user_id = config['configurable'].get("user_id")
    user_info = store.get(("users",),user_id)
    return str(user_info.value)


from typing import Dict, Any
    

@tool 
def save_user_info(user_info: Dict[str, Any], config: RunnableConfig) -> str:
    """
    Save structured user information as key-value pairs.

    Input:
    - user_info (dict): Example {"name": "Alice", "age": 30}.
    - config (RunnableConfig): contains user_id for storage.

    Output:
    - Confirmation string.

    When to use:
    - Use whenever the user shares personal details (name, preferences, etc.) that should be remembered for future interactions.

    """
    store = get_store()
    user_id = config['configurable'].get("user_id")
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info "


#final tool list 
tools = [
    save_user_info,
    get_user_info,
    arxiv_search,
    read_tool,
    add_human_in_the_loop(write_tool),
    list_tool,
    tavily_search,
    wikipedia_tool,
    youtube_search_tool,
    youtube_transcript_tool,
    add_event,
    list_events,
    read_webpage,
    generate_pdf,
    shopping_search,
    add_human_in_the_loop(create_ticket),
    list_tickets,
    get_ticket_details,  
    news_search,
    add_human_in_the_loop(update_ticket),
    repl_tool
]