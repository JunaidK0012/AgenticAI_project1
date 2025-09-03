import os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')
llm_mini = ChatGoogleGenerativeAI(model = 'gemini-1.5-flash')

from datetime import datetime
CURRENT_TIME_IST = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")