import streamlit as st
import os
import sys
import json
import traceback
from datetime import datetime


# Ensure parent directory is visible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import graph
from src.memory.sqlite_memory import save_thread_title
from src.utils.helper import (
    init_session_state,
    get_config,
    generate_conversation_title,
    reset_chat,
    convert_state_messages,
    add_thread,
    load_conversation,
)
from frontend.conversation_manager import assistant_stream_response, handle_interrupted_action
from src.config.settings import user_id

# -------------------- Page Config --------------------
st.set_page_config(page_title="LangGraph Assistant", page_icon="🤖", layout="wide")

# -------------------- Theme Toggle --------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

def toggle_theme():
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"


# -------------------- CSS Themes --------------------
light_theme = """
<style>
body { font-family:'Inter',sans-serif;background-color:#f8fafc;color:#0f172a;transition: background-color 0.4s ease, color 0.4s ease; }
.chat-wrapper{max-width:900px;margin:0 auto;padding:1.5rem 1rem 5rem;max-height:70vh;overflow-y:auto;scroll-behavior:smooth;}
.message{display:flex;align-items:flex-start;margin-bottom:1.2rem;animation:fadeIn .3s ease-in-out;position:relative;}
.bubble{padding:.9rem 1.2rem;border-radius:1rem;line-height:1.5;word-wrap:break-word;
box-shadow:0 3px 6px rgba(0,0,0,0.06);max-width:80%;transition: background-color 0.4s ease, color 0.4s ease, border-color 0.4s ease;}
.bubble.user{background:linear-gradient(135deg,#2563eb,#1e40af);color:white;margin-left:auto;position:relative;}
.bubble.assistant{background-color:#e2e8f0;color:#0f172a;border:1px solid #cbd5e1;position:relative;}
.bubble.user::after {
  content: ""; position: absolute; right: -8px; top: 14px;
  border-width: 8px 0 8px 8px; border-style: solid;
  border-color: transparent transparent transparent #2563eb;
}
.bubble.assistant::after {
  content: ""; position: absolute; left: -8px; top: 14px;
  border-width: 8px 8px 8px 0; border-style: solid;
  border-color: transparent #e2e8f0 transparent transparent;
}
.header{background:linear-gradient(90deg,#2563eb,#1d4ed8);color:white;text-align:center;padding:1rem;
border-radius:.75rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.15);transition: background-color 0.4s ease;}
.footer{text-align:center;color:#64748b;font-size:.85rem;padding:1rem;}
.streaming{background-color:#e2e8f0;color:#0f172a;border-radius:1rem;border:1px solid #cbd5e1;
padding:.9rem 1.2rem;box-shadow:0 2px 6px rgba(0,0,0,0.05);max-width:80%;line-height:1.5;}
.sidebar-btn{background:#e2e8f0;border-radius:.4rem;border:none;color:#1e293b;width:100%;
text-align:left;padding:.4rem .6rem;margin-bottom:.3rem;transition:all .2s ease-in-out;}
.sidebar-btn:hover{background:#cbd5e1;}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}
</style>
"""

dark_theme = """
<style>
body{font-family:'Inter',sans-serif;background-color:#0f172a;color:#f1f5f9;transition: background-color 0.4s ease, color 0.4s ease;}
.chat-wrapper{max-width:900px;margin:0 auto;padding:1.5rem 1rem 5rem;max-height:70vh;overflow-y:auto;scroll-behavior:smooth;}
.message{display:flex;align-items:flex-start;margin-bottom:1.2rem;animation:fadeIn .3s ease-in-out;position:relative;}
.bubble{padding:.9rem 1.2rem;border-radius:1rem;line-height:1.5;word-wrap:break-word;
box-shadow:0 3px 6px rgba(255,255,255,0.05);max-width:80%;transition: background-color 0.4s ease, color 0.4s ease, border-color 0.4s ease;}
.bubble.user{background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:white;margin-left:auto;position:relative;}
.bubble.assistant{background-color:#1e293b;color:#e2e8f0;border:1px solid #334155;position:relative;}
.bubble.user::after {
  content: ""; position: absolute; right: -8px; top: 14px;
  border-width: 8px 0 8px 8px; border-style: solid;
  border-color: transparent transparent transparent #3b82f6;
}
.bubble.assistant::after {
  content: ""; position: absolute; left: -8px; top: 14px;
  border-width: 8px 8px 8px 0; border-style: solid;
  border-color: transparent #1e293b transparent transparent;
}
.header{background:linear-gradient(90deg,#1e3a8a,#1d4ed8);color:white;text-align:center;padding:1rem;
border-radius:.75rem;margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.3);transition: background-color 0.4s ease;}
.footer{text-align:center;color:#94a3b8;font-size:.85rem;padding:1rem;}
.streaming{background-color:#1e293b;color:#e2e8f0;border-radius:1rem;border:1px solid #334155;
padding:.9rem 1.2rem;box-shadow:0 2px 6px rgba(0,0,0,0.05);max-width:80%;line-height:1.5;}
.sidebar-btn{background:#1e293b;border-radius:.4rem;border:none;color:#e2e8f0;width:100%;
text-align:left;padding:.4rem .6rem;margin-bottom:.3rem;transition:all .2s ease-in-out;}
.sidebar-btn:hover{background:#334155;}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}
</style>
"""

# Smooth dot animation for streaming
streaming_animation_css = """
<style>
.dot-typing {
  display:inline-block;
  width: 1.2rem;
  text-align:left;
  font-weight:bold;
}
.dot-typing::after {
  content: '⋯';
  animation: dots 1.5s steps(5, end) infinite;
}
@keyframes dots {
  0%, 20% { color: rgba(0,0,0,0) }
  40% { color: gray }
  60% { color: gray }
  80%, 100% { color: rgba(0,0,0,0) }
}
</style>
"""

st.markdown(dark_theme if st.session_state["theme"] == "dark" else light_theme, unsafe_allow_html=True)
st.markdown(streaming_animation_css, unsafe_allow_html=True)

# -------------------- Session Initialization --------------------
try:
    init_session_state()
except Exception:
    st.error("❌ Failed to initialize session state.")
    st.stop()
try:
    add_thread(st.session_state['thread_id'],topic="New Conversation")
except Exception:
    st.error("❌ Failed to start new chat.")
    st.stop()
try:
    CONFIG = get_config(st.session_state["thread_id"], user_id)
except Exception:
    st.error("❌ Failed to load configuration.")
    st.stop()

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("## 💬 LangGraph Assistant")

    if st.button("🌗 Toggle Theme", use_container_width=True):
        toggle_theme()
        st.rerun()

    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    search_query = st.text_input("🔍 Search conversations", placeholder="Type to search...")
    st.markdown("### My Conversations")

    filtered_threads = [
        thread for thread in st.session_state["chat_threads"]
        if search_query.lower() in thread["topic"].lower()
    ]

    for thread in filtered_threads:
        try:
            if st.button(f"💭 {thread['topic']}", key=thread["thread_id"], use_container_width=True):
                st.session_state["thread_id"] = thread["thread_id"]
                messages = load_conversation(graph, thread["thread_id"])
                st.session_state["message_history"] = convert_state_messages(messages)
        except Exception:
            st.warning(f"⚠️ Could not load: {thread['topic']}")

    if len(st.session_state["message_history"]) > 0:
        export_format = st.radio("Export Format", ["Text", "JSON"], horizontal=True)
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if export_format == "Text":
            chat_text = "\n\n".join(
                [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state["message_history"]]
            )
            st.download_button("💾 Download (.txt)", chat_text, f"{filename}.txt")
        else:
            chat_json = json.dumps(st.session_state["message_history"], indent=2)
            st.download_button("💾 Download (.json)", chat_json, f"{filename}.json")

# -------------------- Header --------------------
st.markdown("""
<div class="header">
    <h1>🤖 Agentic AI Chatbot</h1>
    <p>Ask anything — your multi-model assistant is ready to help.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Chat Container --------------------
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
for msg in st.session_state["message_history"]:
    role_class = "assistant" if msg["role"] == "assistant" else "user"
    st.markdown(
        f'<div class="message"><div class="bubble {role_class}">{msg["content"]}</div></div>',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Handle Interrupts --------------------
if "resume_action" in st.session_state:
    response_placeholder = st.empty()
    response_placeholder.markdown('<div class="streaming"><span class="dot-typing"></span></div>', unsafe_allow_html=True)
    streamed_output = ""
    for chunk in handle_interrupted_action(graph, CONFIG):
        streamed_output += chunk
        response_placeholder.markdown(
            f'<div class="streaming">{streamed_output}<span class="dot-typing"></span></div>',
            unsafe_allow_html=True,
        )
    response_placeholder.markdown(f'<div class="streaming">{streamed_output}</div>', unsafe_allow_html=True)
    st.session_state["message_history"].append({"role": "assistant", "content": streamed_output})
# -------------------- Chat Input --------------------
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    st.markdown(f'<div class="message"><div class="bubble user">{user_input}</div></div>', unsafe_allow_html=True)

    if len(st.session_state["message_history"]) == 1:
        try:
            title = generate_conversation_title(user_input)
            for thread in st.session_state["chat_threads"]:
                if thread["thread_id"] == st.session_state["thread_id"]:
                    thread["topic"] = title
            save_thread_title(st.session_state["thread_id"], title)
        except Exception:
            st.warning("⚠️ Failed to generate title.")

    try:
        with st.spinner("🤖 Thinking..."):
            response_placeholder = st.empty()
            response_placeholder.markdown('<div class="streaming"><span class="dot-typing"></span></div>', unsafe_allow_html=True)
            streamed_output = ""
            for chunk in assistant_stream_response(graph, user_input, CONFIG):
                streamed_output += chunk
                response_placeholder.markdown(
                    f'<div class="streaming">{streamed_output}<span class="dot-typing"></span></div>',
                    unsafe_allow_html=True,
                )
            response_placeholder.markdown(f'<div class="streaming">{streamed_output}</div>', unsafe_allow_html=True)

        st.session_state["message_history"].append({"role": "assistant", "content": streamed_output})

    
    except Exception as e:
        st.error(f"❌ Assistant failed: {e}")
        print(traceback.format_exc())

# -------------------- Footer --------------------
st.markdown('<div class="footer">Built with ❤️ using LangGraph + Streamlit</div>', unsafe_allow_html=True)
