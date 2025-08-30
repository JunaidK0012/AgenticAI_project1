from .arxiv_tool import arxiv_search
from .file_tools import read_tool,write_tool,list_tool
from .human_in_the_loop import add_human_in_the_loop
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from .youtube_tool import youtube_transcript_tool
from .pdf_tool import generate_pdf
from .news_tool import news_search
from langchain_core.tools import Tool,tool
import requests
from langchain_experimental.utilities import PythonREPL
from langchain_community.document_loaders import WebBaseLoader
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




from pydantic import BaseModel

python_repl = PythonREPL()

class PythonREPLInput(BaseModel):
    code: str

repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Input should be Python code as a string.",
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
@tool
def shopping_search(query: str) -> str:
    """
    Search for shopping/product links online.

    Input:
    - query (str): Product name or description.

    Output:
    - List of shopping/product links.
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

import sqlite3
from langchain_core.tools import tool

# --- Setup DB ---
ticket_conn = sqlite3.connect("tickets.db", check_same_thread=False)
ticket_conn.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT
)
""")

# --- Create Ticket ---
@tool
def create_ticket(title: str, description: str) -> str:
    """
    Create a new support ticket.

    Input:
    - title (str): Short title of the issue
    - description (str): Detailed description of the issue

    Output:
    - Confirmation message with ticket ID
    """
    with ticket_conn:
        cur = ticket_conn.execute(
            "INSERT INTO tickets (title, description, status) VALUES (?, ?, ?)",
            (title, description, "open")
        )
        ticket_id = cur.lastrowid
    return f"✅ Ticket #{ticket_id} created: {title} (status: open)"

# --- List Tickets ---
@tool
def list_tickets() -> str:
    """
    List all tickets with their status.
    """
    cur = ticket_conn.execute("SELECT id, title, status FROM tickets ORDER BY id DESC")
    rows = cur.fetchall()
    if not rows:
        return "📭 No tickets found."
    return "\n".join([f"#{row[0]}: {row[1]} [{row[2]}]" for row in rows])

# --- Get Ticket Details ---
@tool
def get_ticket_details(ticket_id: int) -> str:
    """
    Retrieve full details of a specific ticket.

    Input:
    - ticket_id (int): ID of the ticket

    Output:
    - Title, description, and status of the ticket
    """
    cur = ticket_conn.execute(
        "SELECT title, description, status FROM tickets WHERE id = ?",
        (ticket_id,)
    )
    row = cur.fetchone()
    if not row:
        return f"❌ Ticket #{ticket_id} not found."
    return f"📌 Ticket #{ticket_id}\nTitle: {row[0]}\nDescription: {row[1]}\nStatus: {row[2]}"

# --- Update Ticket ---
@tool
def update_ticket(ticket_id: int, status: str) -> str:
    """
    Update the status of a ticket.

    Input:
    - ticket_id (int): ID of the ticket
    - status (str): New status (e.g., open, in-progress, closed)

    Output:
    - Confirmation message
    """
    with ticket_conn:
        cur = ticket_conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        if cur.rowcount == 0:
            return f"❌ Ticket #{ticket_id} not found."
    return f"✅ Ticket #{ticket_id} updated to status: {status}"


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
    add_human_in_the_loop(repl_tool),
    add_event,
    list_events,
    read_webpage,
    generate_pdf,
    shopping_search,
    create_ticket,
    list_tickets,
    get_ticket_details,  # 👈 new tool
    update_ticket,
    news_search,

]