import streamlit as st 
import os
import uuid
import sys
from langgraph.types import Command

from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from langgraph.prebuilt.interrupt import HumanInterruptConfig,HumanInterrupt
from langgraph.types import interrupt
# Add parent directory to sys.path so Python can see main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import graph,generate_conversation_title
from graph_builder import retrieve_all_threads,save_thread_title

# -------------------- utility function -----------------------------

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
            messages = load_conversation(thread["thread_id"])
        except Exception as e:
            st.error("❌ Could not load this conversation. Please refresh.")

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

#_________________________________________________________________________
def ai_only_stream(user_input: str):
    

    for event in graph.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
        stream_mode="updates",
    ):
        if "__interrupt__" in event:
           
            action = event['__interrupt__'][0].value[0]['action_request']['action']
            args = event['__interrupt__'][0].value[0]['action_request']['args']
        
            st.markdown(f"Assistant wants to use the tool `{action}` ")
            st.json(args)

            col1, col3 = st.columns(2)

            # define callback
            def accept_action():
                st.session_state["resume_action"] = {"type": "accept"}

            def deny_action():
                st.session_state["resume_action"] = {"type": "reject"}

            if col1.button("✅ Allow", on_click = accept_action):
                pass  # button itself triggers callback

            elif col3.button("❌ Deny",on_click = deny_action):
                pass


        # Tool event: show in chat UI
        elif "__interrupt__" not in event:
            for node,data in event.items():
                message = data.get('messages',[])
                if isinstance(message, AIMessage):
                    yield message.content
                elif isinstance(message, list) and message and isinstance(message[0], ToolMessage):
                    with st.status("Tools"):
                        for tool_msg in message:
                            st.info(f"🔧 **Using tool:** `{tool_msg.name}`")
                else:
                    pass

# ______________MAIN APP____________________________

user_input = st.chat_input("Type Here")
CONFIG = {'configurable': {'thread_id':st.session_state['thread_id']}}

# after event loop, check if resume_action exists
if "resume_action" in st.session_state:
    decision = st.session_state.pop("resume_action")  # remove after use
    with st.chat_message("assistant"):
        # stream assistant response after decision
        for event in graph.stream(Command(resume=[decision]), config=CONFIG, stream_mode="updates"):
           
            for node, data in event.items():
                messages = data.get("messages", [])
                if isinstance(messages, AIMessage):
                    
                    st.write(messages.content)   # shows assistant text
                elif isinstance(message, list) and message and isinstance(message[0], ToolMessage):
                    with st.status("Tools"):
                        for tool_msg in message:
                            st.info(f"🔧 **Using tool:** `{tool_msg.name}`")
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
        
        
        ai_message = st.write_stream(ai_only_stream(user_input))
        # Save assistant message 
        st.session_state["message_history"].append(
            {"role": "assistant", "content": ai_message})



