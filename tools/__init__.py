from .arxiv_tool import arxiv_search
from .file_tools import read_tool,write_tool,list_tool
from .human_in_the_loop import add_human_in_the_loop
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import YouTubeSearchTool,WikipediaQueryRun

load_dotenv()

#web search
web_search_tool = TavilySearch(max_results=2)

#wikipedia
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(load_all_available_meta=True))

#Youtube
youtube_tool = YouTubeSearchTool()

#final tool list 
tools = [
    arxiv_search,
    read_tool,
    add_human_in_the_loop(write_tool),
    list_tool,
    web_search_tool,
    wikipedia_tool,
    youtube_tool
]