# QA-agent — Gold Market Support Agent

A LangGraph-powered support assistant that answers gold/macro market
questions using live financial data and web search, falls back to a
RAG knowledge base and human-support ticketing for anything outside its
domain, and remembers relevant facts about each user across sessions.

Backend is FastAPI + Postgres (with `pgvector`), the agent graph is built
with LangGraph, and LLM calls go through Groq.

**NOTE**: There are 2 versions:
1. **The agent core**: which is just langgraph flow.
2. **The full agent**: which is the langgraph flow + backend & client; This `README.md` is for the **full agent**.

## Client

<!-- Add your client screenshot below -->

![Client screenshot](./Screenshot.png)

---

## How it works

Every user message goes through a graph of nodes (see `src/graph.py`):

```mermaid
flowchart RL
    USER_INPUT(User Input) --> QUESTION_CLASSIFIER{"Can the main agent answer?"}

    QUESTION_CLASSIFIER -->|No| DEPARTMENT_CLASSIFIER_AND_TICKET_DATA_EXTRACTOR[Department Classifier and etract data for ticket]
    DEPARTMENT_CLASSIFIER_AND_TICKET_DATA_EXTRACTOR --> CLASSIFIED_DEPARTMENT(Create Ticket for department)
    QUESTION_CLASSIFIER -->|Yes| AGENT["Agent"]

    subgraph Agent_pipeline [Agent pipeline]
        AGENT --> TOOLS["Other tools"]
        TOOLS --> |if tool limit is not reached| AGENT
        AGENT --> |if tool limit is reached| TOOLS_LIMIT
        TOOLS_LIMIT["no more tool use"] --> AGENT
    end

    AGENT --> VALIDATE_AGENT_RESPONSE{Is Agent Response Ok?}

    
    VALIDATE_AGENT_RESPONSE -->|No| DEPARTMENT_CLASSIFIER_AND_TICKET_DATA_EXTRACTOR
    VALIDATE_AGENT_RESPONSE -->|Yes| IS_DATA_WORTH_TO_SAVE 

    subgraph DATABASE_PIPELINE [database pipeline]
        IS_DATA_WORTH_TO_SAVE{"Extracting chat and check if it is worth to save?"} --> |Yes| SAVE_TO_DATABASE["Save data to database"]
    end

    SAVE_TO_DATABASE --> DONE_FROM_AGENT("done from agent")
    IS_DATA_WORTH_TO_SAVE --> |no| DONE_FROM_AGENT("done from agent")
```

1. **`question_classifier_node`** — a small LLM decides whether the request
   is in-domain (gold prices, currencies, macro events → `"rag"`) or should
   be **escalated** to human support (`"escalate"`).
2. **`main_agent_node`** — the main LLM, bound to three tools:
   - `financial_data_tool` — reads OHLCV price history from Postgres
   - `retriever_tool` — semantic search over a `pgvector` knowledge base
   - `search_tool` (Tavily) — finance-scoped web search
   A `tool_calls_count` cap (`MAX_TOOL_CALLS`) prevents infinite tool loops;
   once hit, `tool_limit_reached_node` forces the agent to answer with what
   it already has.
3. **`main_agent_response_validator_node`** — regex-checks the agent's
   answer for PII (SSN, credit card, email, phone, URLs) before it's
   allowed to reach the user. A "bad" response is redirected into the
   escalation/ticket flow instead of being shown as-is.
4. **`building_classifier_and_ticket_node`** — for escalated requests, an
   LLM extracts topic/budget/job/goals and picks which support "building"
   (department) should receive it, then **`insert_ticket_node`** writes a
   `Ticket` row.
5. **`extract_data_after_agent_node`** — after a successful (non-escalated)
   exchange, an LLM decides whether anything is worth remembering long-term
   (preferences, budget, goals, etc.) and stores it in the `AsyncPostgresStore`,
   keyed per user. `main_agent_node` semantically searches this store on
   every turn and injects relevant memories into the system prompt.

State shared between nodes is defined in `src/state.py` (`SupportState`).

---

## Features

- **JWT auth** — signup/login, first registered user becomes admin
- **Streaming chat over WebSocket** — token-by-token agent responses
- **Tool-using agent** — financial data, RAG retrieval, web search
- **PII/hallucination guard** on every agent response before it reaches the user
- **Automatic support ticketing** for out-of-domain requests
- **Long-term per-user memory** via semantic search over past conversations
- **RAG ingestion pipeline** — admin file upload → chunk → embed → `pgvector`
- **ETL pipeline** — pulls OHLCV data from Yahoo Finance into Postgres for the financial data tool
- **Message feedback (👍/👎)** — like/dislike any assistant message (see below)

---

## Project structure

```
agent_full/
├── config.py                    # env-based Settings + SUPPORT_BUILDINGS config
├── src/
│   ├── state.py                 # SupportState / TypedDicts shared across graph nodes
│   ├── graph.py                 # builds and compiles the LangGraph agent
│   ├── chat.py                  # chat_stream(): drives the graph, yields ws chunks
│   ├── helpers.py                # safe_structured_invoke() retry wrapper
│   ├── prompts.py                # all system prompts
│   ├── auth/                    # signup/login, JWT, password hashing, deps
│   ├── database/                # SQLAlchemy models/schemas + engine (tickets, feedback)
│   ├── nodes/                   # one file per graph node
│   ├── tools/                   # financial_data_tool, retriever_tool, search_tool
│   ├── rag/                     # vector_store.py (retriever), ingest.py (chunk+embed)
│   ├── etl/                     # extract (yfinance) → transform → load (Postgres)
│   └── api/                     # FastAPI routers: auth, chat (ws), upload, tickets, data, feedback
```

---

## Tech stack

| Layer | Tech |
|---|---|
| API | FastAPI, WebSockets |
| Agent orchestration | LangGraph |
| LLMs | Groq (`langchain_groq`) |
| Embeddings | Ollama (`langchain_ollama`) |
| Vector store / long-term memory | Postgres + `pgvector` (`langchain_postgres`, `AsyncPostgresStore`) |
| Short-term memory (checkpointing) | `AsyncPostgresSaver` |
| Relational data | SQLAlchemy + Postgres |
| Web search | Tavily |
| Market data | `yfinance` |
| Auth | `python-jose` (JWT) + `passlib`/`bcrypt` |

---

## Setup

### 1. Requirements

- Python 3.11+
- A running Postgres instance with the `vector` extension available (created automatically on first connect)
- Ollama running locally (or reachable) for embeddings
- API keys: Groq, Tavily

### 2. Environment variables

Create a `.env` file in `agent_full/`:

| Variable | Required | Default | Notes |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Main + classifier LLM calls |
| `GROQ_MODEL_NAME` | | `openai/gpt-oss-20b` | Main agent model |
| `GROQ_CLASSIFY_MODEL_NAME` | | `meta/llama-3.1-8b-instant` | Classifier/extractor nodes |
| `OLLAMA_EMBEDDING_MODEL_NAME` | ✅ | — | Used for RAG + long-term memory embeddings |
| `POSTGRESQL_DATABASE_LINK` | ✅ | `INVALID_LINK` | e.g. `postgresql://user:pass@host:5432/db` |
| `TAVILY_API_KEY` | ✅ | — | Web search tool |
| `JWT_SECRET` | ✅ | — | Signs access tokens |
| `MAX_TOOL_CALLS` | | `5` | Cap on tool calls per turn |
| `IS_DEVELOPMENT` | | `true` | |
| `USE_PROXY` / `PROXY_LINK` | | `false` / — | Set if outbound calls need a proxy |

### 3. Install & run

```bash
pip install -r requirements.txt   # or your preferred env manager

uvicorn src.api.server:app --reload
```

On startup, `lifespan()` runs `migrate_users()` and `migrate_tickets_and_feedback()`,
creating the `users`, `tickets`, and `feedback` tables if they don't exist.
The `vector` extension and `pgvector` collection are created lazily the
first time the engine/vector store is used.

---

## API overview

### Auth (`/auth`)
| Method | Path | Notes |
|---|---|---|
| `POST` | `/auth/signup` | First account created becomes `admin` automatically |
| `POST` | `/auth/login` | Form-encoded (`OAuth2PasswordRequestForm`), returns a JWT |

### Chat
| Method | Path | Notes |
|---|---|---|
| `WS` | `/ws/chat?token=<jwt>` | Send plain text messages, receive `{type: "token"/"tool_call"/"done"}` chunks streamed from the graph |

### Admin
| Method | Path | Notes |
|---|---|---|
| `POST` | `/admin/upload-file` | Admin-only. Accepts `.txt`/`.md`, chunks + embeds into the RAG vector store |
| `GET` | `/admin/tickets` | Admin-only. Lists escalated support tickets, filterable by `user_id` |

### Data
| Method | Path | Notes |
|---|---|---|
| `GET` | `/data/{asset}` | Auth required. Returns recent OHLCV rows for `gold`/`dxy`/`silver`/`oil`/`sp500` |

### Feedback
| Method | Path | Notes |
|---|---|---|
| `POST` | `/chat/feedback` | Auth required. Rate a single assistant message `+1`/`-1`, see below |

---

## Message feedback (👍 / 👎)

Any authenticated user can rate a single assistant message. This is the
first building block toward collecting preference data (e.g. for a future
DPO fine-tuning pass or feedback-driven routing).

**1. Getting a `message_id`** — each streamed token chunk over `/ws/chat`
now includes the id of the message it belongs to:

```json
{ "type": "token", "content": "...", "message_id": "run-abc123" }
```

All chunks belonging to the same assistant message share the same
`message_id` — the client should keep the **last** one it sees per message.

**2. Submitting a rating:**

```
POST /chat/feedback
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "thread_id": "<same thread_id used for the websocket session>",
  "message_id": "run-abc123",
  "rating": 1,           // +1 = like, -1 = dislike
  "comment": "optional free-text note"
}
```

```json
{ "status": "ok", "feedback_id": 42 }
```

`rating` only accepts `-1` or `1` — there's no neutral/0 state by design.
`thread_id` is currently the same value as `user_id` (see `chat.py`'s
`config["configurable"]["thread_id"]`); if multiple concurrent threads per
user are added later, make sure the client tracks the real `thread_id`.

This is intentionally minimal — there's no admin "view all feedback"
endpoint or dataset export yet. Add one on top of the `Feedback` model
(`src/database/models.py`) when you're ready to build a preference dataset.

---

## Known gaps / things to harden before production

- CORS is wide open (`allow_origins=["*"]`)
- No promote-to-admin route — the only way to get a second admin is direct DB access
- `financial_data_tool` reads whatever is in `ohlcv_<asset>` tables — the ETL pipeline (`src/etl/`) needs to be run/scheduled separately to keep that data fresh
- No rate limiting on `/chat/feedback` or the websocket endpoint
