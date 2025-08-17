import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph_builder import build_graph

# Build agentic graph
graph = build_graph()

# --- Streamlit UI ---
st.set_page_config(page_title="Agentic AI Assistant", layout="wide")
st.title("🤖 Agentic AI Research Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "graph_config" not in st.session_state:
    st.session_state.graph_config = {"configurable": {"thread_id": "web_ui"}}
if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None


# --- Chat input ---
user_input = st.chat_input("Ask me anything (e.g., 'search AI papers on arxiv')")
if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Run graph
    result = graph.invoke({"messages": st.session_state.messages}, st.session_state.graph_config)

    # If interrupt request is present, capture it
    if isinstance(result, list) and result and "action_request" in result[0]:
        st.session_state.pending_interrupt = result[0]
    else:
        st.session_state.messages.extend(result["messages"])


# --- Display chat messages ---
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)


# --- HITL interrupt UI ---
if st.session_state.pending_interrupt:
    interrupt = st.session_state.pending_interrupt
    action = interrupt["action_request"]["action"]
    args = interrupt["action_request"]["args"]

    st.warning(f"⚠️ Tool call pending review: **{action}({args})**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Accept"):
            for chunk in graph.stream(
                Command(resume=[{"type": "accept"}]),
                st.session_state.graph_config,
            ):
                st.session_state.messages.extend(chunk.get("messages", []))
            st.session_state.pending_interrupt = None
            st.experimental_rerun()

    with col2:
        if st.button("✏️ Edit Args"):
            new_args = st.text_area("Edit tool args (JSON)", value=str(args))
            if st.button("Submit Edited Args"):
                for chunk in graph.stream(
                    Command(resume=[{"type": "edit", "args": {"args": eval(new_args)}}]),
                    st.session_state.graph_config,
                ):
                    st.session_state.messages.extend(chunk.get("messages", []))
                st.session_state.pending_interrupt = None
                st.experimental_rerun()

    with col3:
        if st.button("💬 Respond Instead"):
            feedback = st.text_area("Write your feedback")
            if st.button("Submit Feedback"):
                for chunk in graph.stream(
                    Command(resume=[{"type": "response", "args": feedback}]),
                    st.session_state.graph_config,
                ):
                    st.session_state.messages.extend(chunk.get("messages", []))
                st.session_state.pending_interrupt = None
                st.experimental_rerun()
