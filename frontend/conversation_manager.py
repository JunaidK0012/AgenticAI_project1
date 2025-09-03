import streamlit as st 
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langsmith import traceable

def assistant_stream_response(graph ,user_input: str,config: dict):
    
    for event in graph.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
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