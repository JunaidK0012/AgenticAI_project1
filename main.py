from langchain_core.messages import HumanMessage
from graph_builder import build_graph

from langgraph.types import Command

graph = build_graph()

#initial_state = {"messages": [HumanMessage(content="write a python file(prime.py) for checking weather the number is prime number or not ")]}
#config = {"configurable": {"thread_id":"40"}}


def ai_response(user_input,config):
    chunk = graph.stream({'messages': [HumanMessage(content = user_input)]},config,stream_mode='messages')
    return chunk['messages'][-1].content
    


