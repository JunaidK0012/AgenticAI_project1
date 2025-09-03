from src.memory.db_connection import get_tickets_connection

from langchain_core.tools import tool

# --- Setup DB ---
ticket_conn = get_tickets_connection()
ticket_conn.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT
)
""")


# --- Create Ticket ---
@tool
def create_ticket(title: str, description: str) -> str:
    """
    Create a new support ticket.

    Input:
    - title (str): Short title of the issue
    - description (str): Detailed description of the issue

    Output:
    - Confirmation message with ticket ID
    """
    with ticket_conn:
        cur = ticket_conn.execute(
            "INSERT INTO tickets (title, description, status) VALUES (?, ?, ?)",
            (title, description, "open")
        )
        ticket_id = cur.lastrowid
    return f"✅ Ticket #{ticket_id} created: {title} (status: open)"

# --- List Tickets ---
@tool
def list_tickets() -> str:
    """
    List all tickets with their status.
    """
    cur = ticket_conn.execute("SELECT id, title, status FROM tickets ORDER BY id DESC")
    rows = cur.fetchall()
    if not rows:
        return "📭 No tickets found."
    return "\n".join([f"#{row[0]}: {row[1]} [{row[2]}]" for row in rows])

# --- Get Ticket Details ---
@tool
def get_ticket_details(ticket_id: int) -> str:
    """
    Retrieve full details of a specific ticket.

    Input:
    - ticket_id (int): ID of the ticket

    Output:
    - Title, description, and status of the ticket
    """
    cur = ticket_conn.execute(
        "SELECT title, description, status FROM tickets WHERE id = ?",
        (ticket_id,)
    )
    row = cur.fetchone()
    if not row:
        return f"❌ Ticket #{ticket_id} not found."
    return f"📌 Ticket #{ticket_id}\nTitle: {row[0]}\nDescription: {row[1]}\nStatus: {row[2]}"

# --- Update Ticket ---
@tool
def update_ticket(ticket_id: int, status: str) -> str:
    """
    Update the status of a ticket.

    Input:
    - ticket_id (int): ID of the ticket
    - status (str): New status (e.g., open, in-progress, closed)

    Output:
    - Confirmation message
    """
    with ticket_conn:
        cur = ticket_conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        if cur.rowcount == 0:
            return f"❌ Ticket #{ticket_id} not found."
    return f"✅ Ticket #{ticket_id} updated to status: {status}"