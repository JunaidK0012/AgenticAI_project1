import os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI



llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')
