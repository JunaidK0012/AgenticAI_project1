import streamlit as st 
from langgraph.types import Command
from langchain_core.messages import AIMessageChunk,ToolMessageChunk, HumanMessage, AIMessage, ToolMessage
from langsmith import traceable
import traceback
import time

def assistant_stream_response(graph ,user_input: str,config: dict):
    try:
        for stream_mode, chunk in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode=["updates", "messages"],
        ):
      
            if stream_mode == "messages":
                message, metadata = chunk 
                if isinstance(message, AIMessageChunk):
                    yield message.content
                elif isinstance(message, ToolMessage):
                    with st.spinner(f"🔧 Using tool: {message.name}..."):
                        st.toast(f"🧠 Running tool: {message.name}", icon="⚙️")


            elif stream_mode == "updates":
                if "__interrupt__" in chunk:

                    st.info("⚠️ Agent paused: waiting for human input...")

            
                    action = chunk['__interrupt__'][0].value[0]['action_request']['action']
                    args = chunk['__interrupt__'][0].value[0]['action_request']['args']
                
                    show_interrupt_popup(action,args)

    except Exception as e:
        # Detect LLM rate limit / overload
        err_str = str(e)
        if "429" in err_str or "RateLimit" in err_str or "quota" in err_str.lower():
            st.warning("⚠️ The LLM API rate limit was reached. Please wait and try again.")
        elif "503" in err_str or "overload" in err_str.lower():
            st.toast("⚠️ The model is currently overloaded. Please retry in a moment.")
        else:
            st.error("❌ Assistant stream failed. Please retry.")
        print(traceback.format_exc())


@traceable(name = "hitl_handler")
def handle_interrupted_action(graph, config: dict):
    try:
        decision = st.session_state.pop("resume_action")  # remove after use
        streamed_output = ""
        for stream_mode, chunk in graph.stream(Command(resume=[decision]), config=config, stream_mode=["updates", "messages"]):
            if stream_mode == "messages":
                message, metadata = chunk 
                if isinstance(message, AIMessageChunk):
                    yield message.content
                elif isinstance(message, list) and message and isinstance(message[0], ToolMessage):
                    with st.spinner(f"🔧 Using tool: {message.name}..."):
                        st.toast(f"🧠 Running tool: {message.name}", icon="⚙️")
            elif stream_mode == "updates":
                if "__interrupt__" in chunk:
                    time.sleep(0.3)
                    st.info("⚠️ Agent paused: waiting for human input...")

            
                    action = chunk['__interrupt__'][0].value[0]['action_request']['action']
                    args = chunk['__interrupt__'][0].value[0]['action_request']['args']
                
                    show_interrupt_popup(action,args)


    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RateLimit" in err_str or "quota" in err_str.lower():
            st.warning("⚠️ Rate limit hit while resuming action. Please try again soon.")
        elif "503" in err_str or "overload" in err_str.lower():
            st.warning("⚠️ The model is overloaded. Try again later.")
        else:
            st.error("❌ Failed to process interrupted action.")
        print(traceback.format_exc())

def show_interrupt_popup(action, args):
    try:
        @st.dialog("⚠️ Human Review Required")
        def popup():
            st.markdown(f"### 🧠 The assistant wants to use `{action}`")
            st.caption("Review the tool’s parameters below:")
            with st.expander("🔍 Tool arguments"):
                st.json(args)
                                                                                                                                                                
            col1, col2 = st.columns(2)

            # define callback
            def accept_action():
                st.session_state["resume_action"] = {"type": "accept"}

            def deny_action():
                st.session_state["resume_action"] = {"type": "reject"}


            if col1.button("✅ Approve", on_click = accept_action):
                st.rerun()  # button itself triggers callback

            elif col2.button("❌ Deny",on_click = deny_action):
                st.rerun()
        popup()
    except Exception as e:
        st.error("❌ Error showing human review popup.")
        print(traceback.format_exc())