from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from tools import tools
from llm_node import planner_node

#tools
#plannertool

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_graph():
    graph = StateGraph(State)
    checkpointer = InMemorySaver()
    tool_node = ToolNode(tools)
    graph.add_node('planner_node',planner_node)
    graph.add_node('tools',tool_node)

    graph.add_edge(START,'planner_node')
    graph.add_conditional_edges('planner_node',tools_condition)
    graph.add_edge('tools','planner_node')
    return graph.compile(checkpointer=checkpointer)