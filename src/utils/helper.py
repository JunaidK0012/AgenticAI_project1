import streamlit as st 
import os
import uuid
from src.config.settings import llm
from src.memory.sqlite_memory import save_thread_title
from langchain_core.prompts import ChatPromptTemplate
from src.graph.graph_builder import build_graph
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from src.memory.sqlite_memory import retrieve_all_threads

def init_session_state():
    if 'message_history' not in st.session_state:
        st.session_state['message_history'] = []

    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = generate_thread_id()

    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = retrieve_all_threads()

def get_config(thread_id: str):
    return {'configurable': {'thread_id': thread_id}}


def generate_conversation_title(user_message: str) -> str:
    prompt = ChatPromptTemplate([
        ('system','You are a helpful assistant that generates short chat titles (max 5 words).'),
        ('user',"Create a short title for this conversation:\n\n{messages}")
    ]) 

    chain = prompt | llm

    response = chain.invoke({'messages':user_message})

    return response.content.strip()

def generate_thread_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
    # Check if the current chat is empty
    if len(st.session_state.get("message_history", [])) == 0:
        # Do not create a new chat if the latest one is empty
        st.warning("You already have an empty chat.")
        return  
    # Otherwise, create a new thread
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id,topic="New Conversation")
    save_thread_title(thread_id,"New Conversation")
    st.session_state['message_history'] = []


def add_thread(thread_id,topic=None):
    if not any(t['thread_id'] == thread_id for t in st.session_state["chat_threads"]):
        st.session_state["chat_threads"].append({
            "thread_id": thread_id,
            "topic": topic or str(thread_id)
            
        })

def load_conversation(graph,thread_id):
    try:
        state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages', [])
    except Exception as e:
        st.warning(f"Could not load conversation. Please try again.")


def convert_state_messages(state_messages):
    out = []
    for m in state_messages:
        if isinstance(m, HumanMessage):
            out.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            out.append({"role": "assistant", "content": m.content})
    return out