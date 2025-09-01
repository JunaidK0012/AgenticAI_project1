from langchain_core.messages import HumanMessage
from src.graph.graph_builder import build_graph
from config import llm

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

graph = build_graph()

#initial_state = {"messages": [HumanMessage(content="write a python file(prime.py) for checking weather the number is prime number or not ")]}
#config = {"configurable": {"thread_id":"40"}}




    


