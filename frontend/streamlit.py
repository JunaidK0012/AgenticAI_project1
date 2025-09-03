import streamlit as st 
import os
import sys
# Add parent directory to sys.path so Python can see main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import graph
from src.memory.sqlite_memory import retrieve_all_threads,save_thread_title
from src.utils.helper import init_session_state,get_config,generate_conversation_title,reset_chat,convert_state_messages,add_thread,generate_thread_id,load_conversation
from frontend.conversation_manager import assistant_stream_response,handle_interrupted_action

# ----------------------- Session State ---------------------------
init_session_state()

add_thread(st.session_state['thread_id'],topic="New Conversation")

CONFIG = get_config(st.session_state['thread_id'])

#------------------------- Sidebar UI ---------------------------------- 


st.sidebar.header('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("My Conversations")

for thread in st.session_state['chat_threads']:
    
    if st.sidebar.button(thread["topic"],key=thread['thread_id']):

        # Auto-remove empty chats when switching
        if (len(st.session_state.get("message_history", [])) == 0 and 
            any(t["thread_id"] == st.session_state["thread_id"] for t in st.session_state["chat_threads"])):
            st.session_state["chat_threads"] = [
                t for t in st.session_state["chat_threads"]
                if t["thread_id"] != st.session_state["thread_id"]
            ]
            
        st.session_state['thread_id'] = thread["thread_id"]
        try:
            messages = load_conversation(graph,thread["thread_id"])
        except Exception as e:
            st.error("❌ Could not load this conversation. Please refresh.")

        st.session_state['message_history'] = convert_state_messages(messages)

#-------------------------- History ---------------------------------- 

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# ----------------------- Main Loop ------------------------------------

user_input = st.chat_input("Type Here")

handle_interrupted_action(graph,CONFIG)

if user_input: 

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

    
    
  # Assistant streaming block
    with st.chat_message("assistant"):
        
        
        ai_message = st.write_stream(assistant_stream_response(graph,user_input,CONFIG))
        # Save assistant message 
        st.session_state["message_history"].append(
            {"role": "assistant", "content": ai_message})



