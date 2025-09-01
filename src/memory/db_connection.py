

import sqlite3
import os

DB_PATH = os.getenv("CHATBOT_DB_PATH", "chatbot.db")

def get_connection():
    # One shared connection for app lifetime (LangGraph checkpointer needs it)
    return sqlite3.connect(DB_PATH, check_same_thread=False)
