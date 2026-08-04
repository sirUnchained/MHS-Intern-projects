from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.auth.models import migrate as migrate_users
from src.database.models import migrate as migrate_tickets_and_feedback
from src.api.upload_router import router as upload_router
from src.api.chat_router import router as chat_router
from src.api.ticket_router import router as ticket_router
from src.api.data_router import router as data_router
from src.api.feedback_router import router as feedback_router
from src.api.thread_router import router as thread_router

from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate_users()
    migrate_tickets_and_feedback()
    yield


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

# ======================== CORS =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =================================================================


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(ticket_router)
app.include_router(data_router)
app.include_router(feedback_router)
app.include_router(thread_router)


@app.get("/health")
def health():
    return {"status": "ok"}
