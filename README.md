# 🤖 Agentic AI Chatbot  
*A ChatGPT-like Agentic AI assistant with memory, human-in-the-loop, fault tolerance, and Streamlit UI.*  

## 📌 Overview  
This project is a **general-purpose Agentic AI chatbot** that combines conversational intelligence with real-world tool usage. Inspired by ChatGPT, it integrates **short-term and long-term memory, fault-tolerant workflows, and human-in-the-loop supervision** for more reliable and controllable outputs.  

Built using **LangChain, Python, and Streamlit**, the chatbot supports multiple domains such as research, productivity, customer support, and web search — all within an interactive UI.  

---

## 🚀 Features  
- **💡 Memory**:  
  - Short-term memory for context within a session.  
  - Long-term memory for persistent user information and history.  
 
- **🛠️ Tool Integration**:  
  - Academic search (Arxiv, Wikipedia).  
  - Web browsing (DuckDuckGo, Tavily, YouTube search + transcripts, news search).  
  - Productivity tools (events, notes, PDF generation, Python REPL).  
  - Customer support tools (ticket creation, updates, and details).  
  - Shopping search integration.  

- **👨 Human-in-the-Loop**:  
  - Manual review for critical tasks (e.g., writing, ticket management).  
  - Improves reliability and user trust.  

- **⚡ Fault Tolerance**:  
  - Graceful error handling with fallback strategies.  

- **💻 Streamlit UI**:  
  - ChatGPT-like interface for seamless interaction.  

---

## 🧩 Tool List  
```python
tools = [
    save_user_info,
    get_user_info,
    arxiv_search,
    read_tool,
    add_human_in_the_loop(write_tool),
    list_tool,
    duck_search,
    tavily_search,
    wikipedia_tool,
    youtube_search_tool,
    youtube_transcript_tool,
    python_repl,
    add_event,
    list_events,
    read_webpage,
    generate_pdf,
    shopping_search,
    add_human_in_the_loop(create_ticket),
    list_tickets,
    get_ticket_details,  
    add_human_in_the_loop(update_ticket),
    news_search,
]
```

---

## 📸 Demo  


---

## 📁 Project Structure  
```
Agentic-AI-Chatbot/
│
├── frontend/
│ ├── __init__.py
│ ├── conversation_manager.py ← Manages user–agent conversations
│ └── streamlit.py ← Streamlit-based chat UI
│
├── src/
│ ├── __init__.py
│ ├── config/ ← Configuration files
│ ├── graph/ ← Graph logic
│ ├── memory/ ← sqlite memory handling
│ ├── prompts/ ← LLM prompt templates
│ └── utils/ ← Utility functions and helpers
│
├── tools/
│ ├── __init__.py
│ └── (custom tool scripts for integrations like Arxiv, wikipedia, etc.)
│
├── data/ ← Data files, embeddings, or saved chat logs
├── notebooks/ ← Experimentation and development notebooks
│
├── .env ← Environment variables (API keys)
├── .gitignore ← Files and folders to ignore in git
├── app.py ← Backend logic for agent
├── main.py 
├── README.md ← Project documentation
└── requirements.txt ← Dependencies for the project
```
## ⚙️ Installation  

### 1️⃣ Clone the repo  
```bash
git clone https://github.com/your-username/agentic-ai-chatbot.git
cd agentic-ai-chatbot
```

### 2️⃣ Create virtual environment & install dependencies  
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```
### 3️⃣ Create .env file and store necessary API keys there
```bash
GOOGLE_API_KEY = 'YOUR_GEMINI_API_KEY'
TAVILY_API_KEY = 'YOUR_TAVILY_API_KEY'
NEWS_API_KEY = 'YOUR_NEWS_API_KEY'


LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT='https://api.smith.langchain.com'
LANGCHAIN_API_KEY= 'YOUR_LANGCHAIN_API_KEY'
LANGCHAIN_PROJECT='chatbot_project'

pip install -r requirements.txt
```
### 4️⃣ Run the Streamlit app  
```bash
streamlit run app.py
```

---

## 📚 Tech Stack  
- **Python**  
- **Langgraph** (agent orchestration, memory, tool integration)  
- **Streamlit** (chat UI)  
- **APIs**: Arxiv, Wikipedia,Youtube, Tavily, News APIs  

---

## 🔮 Future Improvements  
- Make the Chatbot multimodal (image)  
- Integrate a production level database(postgres,mongodb,redis) 
- Separate the streamlit UI entirely from the backend (microservice)    

---

## 👤 Author  
**Junaid Khan**  
- 💼 [LinkedIn](https://linkedin.com/in/your-link)  
- 💻 [GitHub](https://github.com/your-username)  
- 📧 your.email@example.com  
