import os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-pro')

user_id = "3er"

from datetime import datetime
CURRENT_TIME_IST = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")