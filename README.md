# swiggysense-agent

A small local-first assistant that extracts food intent, queries Swiggy via Playwright, ranks results, and exposes a Telegram interface.

This repository demonstrates a compact multi-agent pattern (intent extraction + search agent + ranking agent). It uses GROQ as the LLM backend in the current configuration and Playwright for browser automation.

Files
- `agent.py` — orchestrator: calls GROQ, generates suggestions, runs searches, and ranks results.
- `swiggy_ui_agent.py` — Playwright-based browser automation that opens Swiggy, types a query, and scrapes restaurant cards.
- `ranking.py` — simple heuristic scoring and output formatting.
- `telegram_bot.py` — a Telegram polling bot that accepts user messages and returns agent results.
- `main.py` — entrypoint that starts the bot.

Getting started (macOS / zsh)

1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers (required for `swiggy_ui_agent.py`)

```bash
python -m playwright install chromium
```

4. Create a `.env` file from the example and add your keys

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY and TELEGRAM_TOKEN
```

5. Start the Telegram bot (local development)

```bash
python main.py
```

Notes & tips
- Playwright runs a real browser. For first runs you'll see a Chromium window; keep `swiggy_profile/` in `.gitignore` if you don't want to commit session data.
- The project currently calls GROQ's chat completions endpoint with the model `llama-3.1-8b-instant` (configured in `agent.py`). If you'd like to switch to another backend (OpenAI, Ollama, etc.), add a small `llm_client` wrapper and update the calls.
- For a web UI and multi-agent orchestration (FastAPI + React + Docker Compose) see the proposed `api/` and `docker-compose.yml` skeleton in the project roadmap (not included here yet).

Security
- Keep `.env` out of version control. Add it to `.gitignore`.
- Be careful with running arbitrary code or tool executors; sandbox or restrict access when exposing APIs.

Contributing
- Small, focused PRs are easiest — e.g., add a FastAPI wrapper, add Docker support, or improve scraping selectors in `swiggy_ui_agent.py`.
