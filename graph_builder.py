from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from tools import tools
from llm_node import planner_node
import sqlite3

conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

def retrieve_all_threads():

    all_threads=set()

    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_graph():
    graph = StateGraph(State)
    tool_node = ToolNode(tools)
    graph.add_node('planner_node',planner_node)
    graph.add_node('tools',tool_node)

    graph.add_edge(START,'planner_node')
    graph.add_conditional_edges('planner_node',tools_condition)
    graph.add_edge('tools','planner_node')
    return graph.compile(checkpointer=checkpointer)