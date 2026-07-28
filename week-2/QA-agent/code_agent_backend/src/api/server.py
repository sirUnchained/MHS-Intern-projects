from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.auth.models import migrate as migrate_users
from src.database.models import migrate as migrate_tickets
from src.api.upload_router import router as upload_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate_users()
    migrate_tickets()
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

app.include_router(auth_router)
app.include_router(upload_router)


@app.get("/health")
def health():
    return {"status": "ok"}
