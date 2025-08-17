from langchain_core.messages import HumanMessage
from graph_builder import build_graph

from langgraph.types import Command

graph = build_graph()

initial_state = {"messages": [HumanMessage(content="write a python file(prime.py) for checking weather the number is prime number or not ")]}
config = {"configurable": {"thread_id":"40"}}

# Run the agent
chunk = graph.invoke(initial_state, config)
print(chunk['messages'][-1].content)
# Interactive loop
user_input = input("Do you accept? (accept/edit/response): ")

for chunk in graph.stream(
    Command(resume=[{"type": user_input}]),
    config
):
    print(chunk)
    print("\n")
