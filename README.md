# AgenticAI Project 🚀

An **agentic AI system** that coordinates multiple specialized agents to perform research, planning, and summarization tasks with LLMs.

---

## ⚡ Features
- Multi-agent architecture (Research, Summarizer, Planner).
- LLM integration (OpenAI / HuggingFace).
- RAG support (vector DB: FAISS/Pinecone).
- REST API (FastAPI).
- Extensible with new tools and agents.
- Experiment tracking with MLflow (optional).
- Data & model versioning with DVC (optional).

---

## 🏗️ Architecture
```
flowchart TD
    User[User Request] --> API[FastAPI Backend]
    API --> Manager[Agent Manager]
    Manager --> ResearchAgent
    Manager --> SummarizerAgent
    Manager --> PlannerAgent
    ResearchAgent --> LLM
    SummarizerAgent --> LLM
    PlannerAgent --> LLM
    LLM --> VectorDB[(Vector Store)]
```

## 🛠️ Setup
```
# Clone repo
git clone https://github.com/<your-username>/AgenticAI_project1
cd AgenticAI_project1
```

## 🚀 Run
```
# Install dependencies
pip install -r requirements.txt


# Start backend
uvicorn src.api.main:app --reload

# Access API docs
http://127.0.0.1:8000/docs

```

# 📦 Docker
```
docker build -t agenticai .
docker run -p 8000:8000 agenticai
```
