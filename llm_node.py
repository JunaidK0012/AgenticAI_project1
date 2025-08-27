from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import tools
from config import llm
from logger import logger

llm_with_tools = llm.bind_tools(tools)

system_prompt = """ 
You are a reasoning agent that uses tools to answer questions.
You must always follow the Thought → Action → Action Input → Observation loop.

"""

def planner_node(state):

    planner_prompt = ChatPromptTemplate([
        ('system',system_prompt),
        MessagesPlaceholder(variable_name='messages')
    ])

    planner = planner_prompt | llm_with_tools
    result = planner.invoke({'messages': state['messages']})



    return ({'messages':result}) 
    