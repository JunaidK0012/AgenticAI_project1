

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


CHATBOT_DB_PATH = os.path.join(DATA_DIR, "chatbot.db")
CALENDAR_DB_PATH = os.path.join(DATA_DIR, "calendar.db")
TICKETS_DB_PATH = os.path.join(DATA_DIR, "tickets.db")




def get_chatbot_connection():
    return sqlite3.connect(CHATBOT_DB_PATH, check_same_thread=False)

def get_calendar_connection():
    return sqlite3.connect(CALENDAR_DB_PATH, check_same_thread=False)

def get_tickets_connection():
    return sqlite3.connect(TICKETS_DB_PATH, check_same_thread=False)
