import streamlit as st 
from langgraph.types import Command
from langchain_core.messages import AIMessageChunk,ToolMessageChunk, HumanMessage, AIMessage, ToolMessage
from langsmith import traceable

def assistant_stream_response(graph ,user_input: str,config: dict):
    
    for stream_mode, chunk in graph.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode=["updates", "messages"],
    ):
        
        if stream_mode == "messages":
            message, metadata = chunk 
            if isinstance(message, AIMessageChunk):
                print("AIMessage")
                yield message.content
            elif isinstance(message, ToolMessage):
                with st.status("Tools"):
                    st.info(f"🔧 **Using tool:** `{message.name}`")

        elif stream_mode == "updates":
            if "__interrupt__" in chunk:

                st.info("⚠️ Agent paused: waiting for human input...")

           
                action = chunk['__interrupt__'][0].value[0]['action_request']['action']
                args = chunk['__interrupt__'][0].value[0]['action_request']['args']
            
                show_interrupt_popup(action,args)



@traceable(name = "hitl_handler")
def handle_interrupted_action(graph, config: dict):
    # after event loop, check if resume_action exists
    if "resume_action" in st.session_state:
        decision = st.session_state.pop("resume_action")  # remove after use
        with st.chat_message("assistant"):
            # stream assistant response after decision
            for event in graph.stream(Command(resume=[decision]), config=config, stream_mode="updates"):
            
                for _,data in event.items():
                    message = data.get("messages", [])
                    if isinstance(message, AIMessage):
                        
                        st.write(message.content)   # shows assistant text
                    elif isinstance(message, list) and message and isinstance(message[0], ToolMessage):
                        with st.status("Tools"):
                            for tool_msg in message:
                                st.info(f"🔧 **Using tool:** `{tool_msg.name}`")


def show_interrupt_popup(action, args):
    @st.dialog("⚠️ Human Review Required")
    def popup():
        st.markdown(f"Assistant wants to use the tool: **{action}**")
        with st.expander("🔍 Tool arguments"):
            st.json(args)
                                                                                                                                                              
        col1, col2 = st.columns(2)

        # define callback
        def accept_action():
            st.session_state["resume_action"] = {"type": "accept"}


        def deny_action():
            st.session_state["resume_action"] = {"type": "reject"}



        if col1.button("✅ Allow", on_click = accept_action):
            st.rerun()  # button itself triggers callback

        elif col2.button("❌ Deny",on_click = deny_action):
            pass
    popup()