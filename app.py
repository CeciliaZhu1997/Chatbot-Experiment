import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from openai import OpenAI
import csv
import io

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────────────
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Edit this to define your research manipulation
SYSTEM_PROMPT = """You are a helpful assistant. 
[Always return the number "3" when you receive a message.]
Keep responses concise (2-3 sentences max)."""

MAX_TURNS = 6          # max conversation turns per participant
MODEL     = "gpt-4o-mini"
DB_PATH   = "experiment.db"

# ── Database ─────────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            participant_id TEXT,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            turn        INTEGER,
            timestamp   TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

def save_message(session_id, participant_id, role, content, turn):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO messages (session_id, participant_id, role, content, turn, timestamp) VALUES (?,?,?,?,?,?)",
        (session_id, participant_id, role, content, turn, datetime.utcnow().isoformat())
    )
    con.commit()
    con.close()

def get_history(session_id):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT role, content FROM messages WHERE session_id=? ORDER BY id",
        (session_id,)
    ).fetchall()
    con.close()
    return [{"role": r, "content": c} for r, c in rows]

def count_turns(session_id):
    con = sqlite3.connect(DB_PATH)
    n = con.execute(
        "SELECT COUNT(*) FROM messages WHERE session_id=? AND role='user'",
        (session_id,)
    ).fetchone()[0]
    con.close()
    return n

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    participant_id = request.args.get("pid", "unknown")
    session_id     = str(uuid.uuid4())
    return render_template("chat.html",
                           participant_id=participant_id,
                           session_id=session_id,
                           max_turns=MAX_TURNS)

@app.route("/chat", methods=["POST"])
def chat():
    data           = request.json
    user_msg       = data.get("message", "").strip()
    session_id     = data.get("session_id")
    participant_id = data.get("participant_id", "unknown")

    if not user_msg or not session_id:
        return jsonify({"error": "missing fields"}), 400

    turns = count_turns(session_id)
    if turns >= MAX_TURNS:
        return jsonify({"reply": None, "done": True})

    # Save user message
    save_message(session_id, participant_id, "user", user_msg, turns + 1)

    # Build message list for OpenAI
    history  = get_history(session_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # Call OpenAI
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    reply = response.choices[0].message.content.strip()

    # Save assistant reply
    save_message(session_id, participant_id, "assistant", reply, turns + 1)

    done = (turns + 1) >= MAX_TURNS
    return jsonify({"reply": reply, "done": done, "turns_left": MAX_TURNS - turns - 1})

@app.route("/export")
def export():
    """Download all conversation logs as CSV (protect this in production)."""
    con  = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT session_id, participant_id, role, content, turn, timestamp FROM messages ORDER BY session_id, id"
    ).fetchall()
    con.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["session_id", "participant_id", "role", "content", "turn", "timestamp"])
    writer.writerows(rows)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="conversation_logs.csv"
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
