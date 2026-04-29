# Chatbot Experiment Platform

A custom AI chatbot platform designed for communication research. Integrates with Qualtrics to support multi-condition persuasion experiments with full conversation logging.

---

## Overview

This platform enables researchers to embed a controlled AI chat interaction within a Qualtrics survey workflow. Participants are redirected from a pre-survey to the chatbot, interact with an AI whose behavior is governed by a researcher-defined system prompt, and are then redirected to a post-survey. All conversations are logged and exportable for analysis.

---

## System Architecture

```
Qualtrics Pre-survey
  → (redirect with pid + condition)
Custom Chatbot Interface (Flask + OpenAI API)
  → (redirect with pid)
Qualtrics Post-survey
```

---

## Features

- Simulates a standard AI chat interface (ChatGPT-style UI)
- Researcher-controlled system prompt, invisible to participants
- Supports multiple experimental conditions (A / B / C)
- Participant ID passed via URL and linked to all conversation records
- Conversation logs stored in SQLite with session ID, participant ID, condition, role, content, turn, and timestamp
- CSV export endpoint for downstream analysis
- Configurable maximum conversation turns

---

## File Structure

```
chatbot_experiment/
├── app.py               # Flask backend
├── requirements.txt     # Python dependencies
├── README.md
└── templates/
    └── chat.html        # Frontend chat interface
```

---

## Setup (Local)

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Set your OpenAI API key**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**3. Run the app**
```bash
python app.py
```

Visit `http://127.0.0.1:5000` to test locally.

---

## Configuration

All key parameters are in `app.py`:

| Variable | Description |
|---|---|
| `SYSTEM_PROMPTS` | Dict of condition-specific system prompts (A / B / C) |
| `MAX_TURNS` | Maximum conversation turns per participant |
| `MODEL` | OpenAI model (default: `gpt-4o-mini`) |

In `templates/chat.html`:

| Variable | Description |
|---|---|
| `RETURN_URL` | Qualtrics post-survey link (include `?pid=` parameter) |

---

## Qualtrics Integration

### Pre-survey → Chatbot

Set the **End of Survey** redirect URL to:
```
https://your-app-url.onrender.com/?pid=${e://Field/ResponseID}&condition=${e://Field/condition}
```

### Condition Assignment (Survey Flow)

```
Set Embedded Data: condition (empty, at top)
↓
Show Block: [pre-survey questions]
↓
Branch If: answer = A → Set Embedded Data condition = A
Branch If: answer = B → Set Embedded Data condition = B
Branch If: answer = C → Set Embedded Data condition = C
↓
End of Survey (redirect to chatbot)
```

### Chatbot → Post-survey

The chatbot redirects participants to the post-survey URL after `MAX_TURNS` is reached. Set `RETURN_URL` in `chat.html` to your post-survey link.

---

## Data Export

Visit `/export` to download all conversation logs as CSV:

```
https://your-app-url.onrender.com/export
```

**Columns:** `session_id`, `participant_id`, `condition`, `role`, `content`, `turn`, `timestamp`

Merge with Qualtrics data using `participant_id` (= Qualtrics `ResponseID`).

---

## Deployment (Render)

1. Push this repository to GitHub
2. Create a new **Web Service** on [Render](https://render.com), connect the repo
3. Set environment variable: `OPENAI_API_KEY`
4. Set start command: `gunicorn app:app`
5. Deploy

> **Note:** Render's free tier does not support persistent disk storage. The SQLite database will reset on each redeploy. For production use, migrate to a persistent database (e.g., PostgreSQL).

---

## Known Limitations

- SQLite data is not persistent on Render free tier — export CSV before redeploying
- The `/export` endpoint is unprotected — add authentication before running with real participants
- Condition assignment relies on Qualtrics URL parameters; verify the full redirect URL before data collection

---

## Dependencies

- Flask
- OpenAI Python SDK
- Gunicorn
