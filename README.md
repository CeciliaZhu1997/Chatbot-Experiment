# AI Persuasion Experiment — Chatbot Platform

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key-here"
python app.py
```

## Before running

1. **app.py** — edit `SYSTEM_PROMPT` with your research prompt
2. **app.py** — set `MAX_TURNS` (default: 6)
3. **templates/chat.html** — replace `RETURN_URL` with your Qualtrics post-survey link

## Qualtrics integration

In Qualtrics, redirect participants using an End of Survey redirect:
```
https://your-app-url.com/?pid=${e://Field/ResponseID}
```

## Data export

Visit `/export` to download all conversation logs as CSV.
Columns: session_id, participant_id, role, content, turn, timestamp

## Deployment (Render.com)

1. Push this folder to a GitHub repo
2. Create a new Web Service on Render, connect the repo
3. Set environment variable: `OPENAI_API_KEY`
4. Start command: `gunicorn app:app`
5. Add `gunicorn` to requirements.txt
