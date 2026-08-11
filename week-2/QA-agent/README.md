# Mana (مانا) — QA Support & Market Analysis Agent

A FastAPI backend built around a [LangGraph](https://github.com/langchain-ai/langgraph) agent that
handles Phase‑1 customer support, retrieves answers from an ingested knowledge base (RAG), pulls
financial market data (gold, silver, oil, DXY, S&P 500), and escalates anything out of scope to a
human‑support ticket queue. Ships with a small vanilla JS/HTML frontend (Persian, RTL) for chat,
an admin knowledge‑base uploader, and a ticket dashboard.

## Client

![Client screenshot](./screenshot.png)

---

## Architecture

```
agent-full/
├── agent/                  LangGraph agent: nodes, tools, prompts, graph wiring
│   ├── graph.py             Builds the StateGraph, wires nodes/edges, sets up Postgres store+checkpointer
│   ├── chat.py               Async entrypoint used by the WebSocket route (agent/chat.py -> chat_stream)
│   ├── state.py               Shared graph state (SupportState, TypedDicts)
│   ├── nodes/                 question_classifier, building_classifier, main_agent, validator,
│   │                           memory (long-term fact extraction), ticket, tool_limit
│   ├── tools/                  retriever_tool (RAG), financial_data_tool, search_tool (Tavily)
│   └── rag/                    vector_store.py / ingest.py — pgvector‑backed retriever + ingestion
│
├── app/                     FastAPI app
│   ├── main.py                App factory, router registration, table migrations on startup
│   ├── core/                   config.py (env settings), engine.py (SQLAlchemy engine + pgvector
│   │                            extension bootstrap), security.py (JWT + bcrypt)
│   ├── deps.py                 get_db / get_current_user / require_admin dependencies
│   └── features/
│       ├── auth/                 signup/login, first user becomes admin automatically
│       ├── chat_threads/         thread CRUD + /chat/ws/chat WebSocket streaming endpoint
│       ├── feedback/              like/dislike on assistant messages
│       ├── tickets/               admin‑only view/delete of escalated support tickets
│       ├── uploads/               admin‑only .txt/.md upload -> chunk -> embed -> pgvector
│       └── market_data/          authenticated read of OHLCV data (/data/{asset})
│
├── etl/                      extract (yfinance) -> transform -> load (Postgres) pipeline for
│                              market data; also `read.py` used by the financial_data_tool
├── db/base.py                 SQLAlchemy declarative Base
└── frontend/                  Static HTML/CSS/JS client (Persian, RTL)
```

**Flow of a chat message:** the graph classifies the question as `rag` (answerable by the Main
Agent's general knowledge/tools) or `escalate` (routed to a building/department and turned into a
support ticket). The Main Agent has three tools available — RAG retriever, financial data lookup,
and finance‑scoped web search — and is capped at `MAX_TOOL_CALLS`. Every agent response is scanned
for PII (SSN, card numbers, emails, phone numbers, URLs) before being shown to the user; if it
matches, the conversation is routed to escalation instead. After a substantive exchange, a
lightweight extraction step decides whether anything is worth saving to long‑term memory
(LangGraph's Postgres‑backed store), which is later retrieved and injected into future turns.

---

## Requirements

- Docker + Docker Compose (recommended), **or** Python 3.11 and a local Postgres 16 with the
  `pgvector` extension available.
- API keys: [Groq](https://console.groq.com/) and/or [Google AI Studio](https://aistudio.google.com/)
  for the LLMs (chat and embeddings), and [Tavily](https://tavily.com/) for the finance web‑search
  tool.
- **Google AI Studio** API key for embeddings (required); the embedding model is specified via
  `GOOGLE_EMBEDDING_MODEL_NAME` (e.g. `models/embedding-001`). Ollama is **no longer** used for
  embeddings.

---

## Quick start (Docker)

1. Copy `.env.example` to `.env` in `agent-full/` and fill in the values (see [Environment
   variables](#environment-variables) below).

2. From `agent-full/`:

   ```bash
   docker compose up -d --build
   ```

3. Seed market data so `/data/{asset}` and the financial data tool have something to return (see
   [Seeding market data](#seeding-market-data)).

4. Open the frontend at `http://localhost:8080` and the API docs at `http://localhost:8000/docs`.

5. Sign up — **the first account created becomes admin automatically**; there's no promote‑to‑admin
   endpoint, so make your first signup count.

## Quick start (local, no Docker)

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Have Postgres 16+ running locally with `CREATE EXTENSION vector;` permitted (the app runs this
   automatically on startup via `app/core/engine.py`, but the extension package itself must be
   installed on the Postgres server).
4. Have a valid Google API key with access to the embedding model you set in `GOOGLE_EMBEDDING_MODEL_NAME`.
5. Copy `.env.example` to `.env`, fill in values, keep `POSTGRESQL_DATABASE_LINK` pointed at
   `127.0.0.1`.
6. `uvicorn app.main:app --reload`
7. Serve `frontend/` with any static file server (or open `frontend/index.html` directly — it talks
   to the backend over the absolute URLs in `frontend/js/config.js`).

---

## Environment variables

Set these in `agent-full/.env`. Example values below are what this project has been run with; blank
means you must supply your own.

| Variable | Example | Notes |
| --- | --- | --- |
| `GROQ_API_KEY` | *(blank — required)* | Needed if using Groq for chat/classification. |
| `GROQ_MODEL_NAME` | `openai/gpt-oss-20b` | Main agent LLM when using Groq. |
| `GROQ_CLASSIFY_MODEL_NAME` | `llama-3.1-8b-instant` | Used for the question classifier and building/ticket classifier nodes — this is the **only** classify‑model variable actually read by `app/core/config.py`. |
| `GOOGLE_API_KEY` | *(blank — required for embeddings)* | Used for the embedding model (and optionally for chat if you wire Google as a provider). |
| `GOOGLE_EMBEDDING_MODEL_NAME` | `models/embedding-001` | **Required.** The embedding model to use for RAG ingestion/retrieval, long‑term memory store, and admin uploads. Must be a model available via the Google AI Studio or Vertex AI API. |
| `GOOGLE_MODEL_NAME` | `gemini-3.6-flash` | (Optional) Chat model if you switch the graph to use Google instead of Groq — not wired by default. |
| `GOOGLE_CLASSIFY_MODEL_NAME` | `gemini-3.6-flash` | (Optional) Classification model if you switch — not wired by default. |
| `TAVILY_API_KEY` | *(blank — required)* | Powers `agent/tools/search_tool.py` (finance‑scoped web search). |
| `POSTGRESQL_DATABASE_LINK` | `postgresql+psycopg://postgres:11111111@127.0.0.1:5432/support_agent_postgres` | Must use the `postgresql+psycopg://` prefix (psycopg v3), not `postgresql://`. Change the host to `postgres` when running via `docker compose` instead of `127.0.0.1`. |
| `IS_DEVELOPMENT` | `false` | Currently declared but not branched on anywhere in the code shown — reserved for future use. |
| `USE_PROXY` | `false` | If `true`, `app/main.py` sets `http_proxy`/`https_proxy` env vars for outbound requests (e.g. Tavily, yfinance). |
| `PROXY_LINK` | `http://127.0.0.1:8889/` | ⚠️ If you run the backend in Docker, `127.0.0.1` resolves to *the container*, not your host — a host‑machine proxy at this address will be unreachable. Either run the proxy inside the same Docker network and point this at that service's name, or use `host.docker.internal` instead of `127.0.0.1` (Docker Desktop) / your host's Docker‑bridge IP (Linux). |
| `MAX_TOOL_CALLS` | `5` | Hard cap on tool calls per turn before the agent is forced to answer with what it already has. |
| `JWT_SECRET` | *(pick something long and random)* | Used to sign auth tokens — treat as a real secret, don't ship the placeholder value in the example above. Generate one with `openssl rand -hex 32`. |

---

## Seeding market data

`/data/{asset}` and the agent's `financial_data_tool` both read from Postgres tables named
`ohlcv_gold`, `ohlcv_dxy`, `ohlcv_silver`, `ohlcv_oil`, `ohlcv_sp500` — nothing populates these
automatically. Run the ETL pipeline manually (or on a schedule) to fetch data from Yahoo Finance and
load it in, e.g. from a Python shell inside the backend container:

```python
from app.core.engine import get_engine
from etl.pipeline import run_pipeline

engine = get_engine()
run_pipeline("GC=F", engine, "ohlcv_gold", start_date="2023-01-01", if_exists="replace")
run_pipeline("DX-Y.NYB", engine, "ohlcv_dxy", start_date="2023-01-01", if_exists="replace")
run_pipeline("SI=F", engine, "ohlcv_silver", start_date="2023-01-01", if_exists="replace")
run_pipeline("CL=F", engine, "ohlcv_oil", start_date="2023-01-01", if_exists="replace")
run_pipeline("^GSPC", engine, "ohlcv_sp500", start_date="2023-01-01", if_exists="replace")
```

Adjust tickers/date ranges as needed; `run_pipeline` also adds an `embedding vector(1536)` column to
each table by default (`add_vector_column=True`), left unused by the current tools but available if
you later want to embed price rows.

---

## Admin: uploading knowledge‑base documents

Log in as the admin account (the first signup), then use the **Admin** page in the frontend, or call
the endpoint directly:

```bash
curl -X POST http://localhost:8000/admin/upload-file \
  -H "Authorization: Bearer <admin JWT>" \
  -F "file=@docs/faq.md"
```

Only `.txt` and `.md` files are accepted. Content is chunked, embedded via
`GOOGLE_EMBEDDING_MODEL_NAME`, and stored in the `RAG_documents_vectores` pgvector collection, which
`retriever_tool` searches against.

---

## Key API routes

| Route | Auth | Purpose |
| --- | --- | --- |
| `POST /auth/signup` | none | Register; first account becomes admin. |
| `POST /auth/login` | none | Returns a bearer JWT. |
| `POST /chat/threads` / `GET /chat/threads` | user | Create / list chat threads. |
| `GET /chat/threads/{id}/messages` | user (owner) | Full message history for a thread. |
| `WS /chat/ws/chat?token=&thread_id=` | user (owner) | Live streaming chat over the LangGraph agent. |
| `POST /chat/feedback` | user | Like/dislike a specific assistant message. |
| `GET /data/{asset}` | user | Recent OHLCV rows for `gold | dxy | silver | oil | sp500`. |
| `GET /admin/tickets` | admin | List escalated support tickets. |
| `DELETE /admin/tickets/{id}` | admin | Delete a ticket (yes, `GET` — see note below). |
| `POST /admin/upload-file` | admin | Ingest a `.txt`/`.md` file into the RAG store. |
| `GET /health` | none | Liveness check, also used by the Docker healthcheck. |

---

## Docker

See `docker-compose.yml` in this directory. It runs four services:

- **postgres** — `pgvector/pgvector:pg16` (a plain `postgres` image won't have the `vector`
  extension available, and startup will fail on `CREATE EXTENSION vector`).
- **backend** — this FastAPI app, built from the `Dockerfile` in this directory.
- **frontend** — static frontend served via nginx, built from `frontend/Dockerfile`.

> **Note:** The `ollama` service is no longer required because embeddings are now provided by Google.
> If you still want to use Ollama for local chat models, you can add it back manually, but it is not
> needed for the core functionality.

```bash
docker compose up -d --build
docker compose logs -f backend
docker compose down            # add -v to also drop the postgres volumes
```

---

## Tech stack

FastAPI · LangGraph · LangChain (Groq / Google integrations) · SQLAlchemy + psycopg (v3) ·
Postgres + pgvector · Tavily · yfinance/pandas (ETL) · Google Vertex AI / AI Studio (embeddings) ·
vanilla JS/HTML/CSS frontend.
