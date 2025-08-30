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

with conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads(
                 thread_id TEXT PRIMARY KEY,
                 topic TEXT
        )

""")

def retrieve_all_threads():
    threads = []
    cursor = conn.execute("SELECT thread_id, topic FROM threads")
    rows = cursor.fetchall()

    for row in rows:
        threads.append({"thread_id": row[0], "topic": row[1] or "New Conversation"})
    return threads

def save_thread_title(thread_id: str, title: str):
    with conn:
        conn.execute("""
            INSERT INTO threads (thread_id, topic)
            VALUES (?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET topic=excluded.topic
        """, (thread_id, title))

from langgraph.types import Command






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