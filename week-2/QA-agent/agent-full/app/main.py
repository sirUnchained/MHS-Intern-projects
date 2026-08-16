from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.features.auth.models import migrate as migrate_users
from app.features.chat_threads.models import migrate as migrate_chat_threads
from app.features.tickets.models import migrate as migrate_tickets
from app.features.feedback.models import migrate as migrate_feedbacks

from app.features.auth.router import router as auth_router
from app.features.uploads.router import router as upload_router
from app.features.chat_threads.router import router as chat_router
from app.features.tickets.router import router as ticket_router
from app.features.market_data.router import router as data_router
from app.features.feedback.router import router as feedback_router
from app.core.config import get_settings
from app.core.logger import setup_logging

from etl.scheduler import start_scheduler, stop_scheduler, refresh_all_market_data_async

import os
import asyncio
import logging

settings = get_settings()

# ======================== LOGGER =========================
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)
# =======================================================

# ======================== PROXY =========================
if settings.USE_PROXY:
    print(type(settings.USE_PROXY))
    print(settings.USE_PROXY)

    print("[INFO] proxy is set")
    os.environ["http_proxy"] = settings.PROXY_LINK
    os.environ["https_proxy"] = settings.PROXY_LINK
# =======================================================


# ======================== MIGRATION =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate_users()
    migrate_chat_threads()
    migrate_feedbacks()
    migrate_tickets()

    # Fire-and-forget: don't block app startup on yfinance calls.
    asyncio.create_task(refresh_all_market_data_async())
    start_scheduler()

    yield

    stop_scheduler()


# =======================================================


# ======================== APP =========================
app = FastAPI(
    title="QA-agent backend",
    description=(
        "Backend for the QA-agent project. Provides user signup/login "
        "with JWT auth, and an admin-only endpoint to upload documents "
        "that get chunked and embedded into the RAG vector store."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
# =======================================================


# ======================== CORS =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =======================================================


# ======================== ROUTES =========================
@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(ticket_router)
app.include_router(data_router)
app.include_router(feedback_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# =======================================================
