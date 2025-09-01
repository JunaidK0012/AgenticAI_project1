from .db_connection import get_connection

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS threads(
                    thread_id TEXT PRIMARY KEY,
                    topic TEXT
            )

    """)
    return conn


def retrieve_all_threads():
    conn = get_connection()
    rows = conn.execute("SELECT thread_id, topic FROM threads").fetchall()
    return[{"thread_id":row[0], "topic":row[1] or "New Conversation"} for row in rows]


def save_thread_title(thread_id: str, title: str):
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO threads (thread_id, topic)
            VALUES (?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET topic=excluded.topic
        """, (thread_id, title))

    