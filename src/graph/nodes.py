from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import tools
from src.config.settings import llm
from src.utils.logger import logger
from src.prompts.system_prompt import system_prompt


llm_with_tools = llm.bind_tools(tools)




def planner_node(state):

    planner_prompt = ChatPromptTemplate([
        ('system',system_prompt),
        MessagesPlaceholder(variable_name='messages')
    ])

    planner = planner_prompt | llm_with_tools
    result = planner.invoke({'messages': state['messages']})



    return ({'messages':result}) 
    