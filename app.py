# backend/app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, Any

# import your LangGraph builder (adapted from your existing files)
from main import build_graph  # build_graph should return compiled graph
from langchain_core.messages import HumanMessage
from langgraph.types import Command

app = FastAPI(title="LangGraph Chat Service")

# allow CORS for frontend (adjust in shared/config)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default; change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# build graph once on startup
@app.on_event("startup")
async def startup_event():
    global graph
    print("Building LangGraph...")
    graph = build_graph()
    print("Graph built.")

# helper: simple non-streaming chat (collects messages)
@app.post("/chat")
async def chat(payload: Dict[str, Any]):
    """
    Simple synchronous endpoint: returns the assistant final content.
    payload: {"messages":[{"role":"user","content":"..."}], "config": {...}}
    """
    try:
        user_text = payload.get("user_input") or (payload.get("messages", [{}])[0].get("content"))

        config = payload.get("config", {})
        # We'll invoke graph to completion (note: may block; for production use background tasks)
        reply  = graph.invoke({"messages":[HumanMessage(content=user_text)]}, config=config)

        return JSONResponse({"assistant": reply})
    
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=str(e))


# SSE streaming endpoint
@app.post("/stream")
async def stream_chat(payload: Dict[str, Any]):
    """
    Streams assistant chunks as Server-Sent Events.
    Expect JSON body: {"user_input": "<text>", "config": {...}}
    """

    user_text = payload.get("user_input") or (payload.get("messages", [{}])[0].get("content"))
    config = payload.get("config", {})

    if not user_text:
        raise HTTPException(status_code=400, detail="user_input required")

    def event_generator():
        try:
            # graph.stream returns an iterator/generator
            for stream_mode, chunk in graph.stream(
                {"messages": [HumanMessage(content=user_text)]},
                config=config,
                stream_mode=["updates", "messages"],
            ):
                if stream_mode == "messages":
                    message, metadata = chunk
                    # yield assistant chunks
                    try:
                        text = message.content
                        # SSE format: "data: <json>\n\n"
                        payload = json.dumps({"type":"message","content": text})
                        yield f"data: {payload}\n\n"
                    except Exception:
                        pass
                elif stream_mode == "updates":
                    # convert updates to events for frontend to show e.g., tool requests
                    payload = json.dumps({"type":"update","update": chunk})
                    yield f"data: {payload}\n\n"
            # stream finished
            yield f"data: {json.dumps({'type':'end'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# HITL resume endpoint (non-streaming or streaming depending on your choice)
@app.post("/resume")
async def resume_action(payload: Dict[str, Any]):
    """
    payload example: {"decision": {"type":"accept"}, "config": {...}}
    This triggers graph.stream(Command(resume=[decision])) and returns streamed updates.
    """
    decision = payload.get("decision")
    config = payload.get("config", {})

    if not decision:
        raise HTTPException(status_code=400, detail="decision required")

    def event_generator():
        try:
            for stream_mode, chunk in graph.stream(Command(resume=[decision]), config=config, stream_mode=["updates","messages"]):
                if stream_mode == "messages":
                    message, metadata = chunk
                    try:
                        text = message.content
                        yield f"data: {json.dumps({'type':'message','content': text})}\n\n"
                    except Exception:
                        pass
                elif stream_mode == "updates":
                    yield f"data: {json.dumps({'type':'update','update': chunk})}\n\n"
            yield f"data: {json.dumps({'type':'end'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
