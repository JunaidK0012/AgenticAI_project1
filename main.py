from langchain_core.messages import HumanMessage
from graph_builder import build_graph
from config import llm

from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate

graph = build_graph()

#initial_state = {"messages": [HumanMessage(content="write a python file(prime.py) for checking weather the number is prime number or not ")]}
#config = {"configurable": {"thread_id":"40"}}


def generate_conversation_title(user_message: str) -> str:
    prompt = ChatPromptTemplate([
        ('system','You are a helpful assistant that generates short chat titles (max 5 words).'),
        ('user',"Create a short title for this conversation:\n\n{messages}")
    ]) 

    chain = prompt | llm

    response = chain.invoke({'messages':user_message})

    return response.content.strip()

    


