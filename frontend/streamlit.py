import streamlit as st 
import os
import uuid
import sys
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
# Add parent directory to sys.path so Python can see main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import graph,generate_conversation_title
from graph_builder import retrieve_all_threads,save_thread_title

# -------------------- utility function -----------------------------

def generate_thread_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
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

def load_conversation(thread_id):
    try:
        state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages', [])
    except Exception as e:
        st.warning(f"Could not load conversation. Please try again.")

 

# -------------------- Session State ---------------------------

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()



add_thread(st.session_state['thread_id'],topic="New Conversation")

#--------------------- Sidebar UI ---------------------------------- 

st.sidebar.header('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("My Conversations")


for thread in st.session_state['chat_threads']:
    if st.sidebar.button(thread["topic"]):
        st.session_state['thread_id'] = thread["thread_id"]
        messages = load_conversation(thread["thread_id"])

        temp_message = []

        for message in messages:
            if isinstance(message,HumanMessage):
                role = 'user'
            elif isinstance(message,AIMessage):
                role = 'assistant'
            else:
                continue
            temp_message.append({'role':role,'content':message.content})

        st.session_state['message_history'] = temp_message
            






#------------------------------------------------------------------------
#loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])



user_input = st.chat_input("Type Here")

if user_input: 

    #if len(st.session_state['message_history']) == 0:
    # First user input → generate topic using LLM
        #title = generate_conversation_title(user_input)
    
        #for thread in st.session_state["chat_threads"]:
            #if thread["thread_id"] == st.session_state["thread_id"]:
                #thread["topic"] = title

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    # Generate a title if this is the first user input
    if len(st.session_state["message_history"]) == 1:
        title = generate_conversation_title(user_input)
        for thread in st.session_state["chat_threads"]:
            if thread["thread_id"] == st.session_state["thread_id"]:
                thread["topic"] = title
    # Persist in DB
    save_thread_title(st.session_state["thread_id"], title)

    
    CONFIG = {'configurable': {'thread_id':st.session_state['thread_id']}}
  # Assistant streaming block
    with st.chat_message("assistant"):
         
        def ai_only_stream():
            for message_chunk, metadata in graph.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())



    # Save assistant message 
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )