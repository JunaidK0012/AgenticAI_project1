from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from tools import tools
from src.graph.nodes import planner_node
from src.memory.sqlite_memory import init_db
conn = init_db()
checkpointer = SqliteSaver(conn=conn)

from langgraph.store.memory import InMemoryStore

store = InMemoryStore() 

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def build_graph():

    """Define and return the chatbot LangGraph."""

    graph = StateGraph(State)
    tool_node = ToolNode(tools)
    graph.add_node('planner_node',planner_node)
    graph.add_node('tools',tool_node)

    graph.add_edge(START,'planner_node')
    graph.add_conditional_edges('planner_node',tools_condition)
    graph.add_edge('tools','planner_node')
    
    return graph.compile(checkpointer=checkpointer,store=store)