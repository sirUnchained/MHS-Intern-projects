from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

from app.deps import require_admin
from app.features.auth.models import User
from agent.rag.ingest import ingest_text
from app.core.config import get_settings

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_EXTENSIONS = {".txt", ".md"}


@router.post(
    "/upload-file",
    summary="Upload a document for the RAG knowledge base (admin only)",
    description=(
        "Accepts a .txt or .md file, splits it into chunks, embeds each "
        "chunk, and stores it in the vector database used by the agent's "
        "retriever tool. Requires an admin JWT in the Authorization header."
    ),
)
async def upload_file(
    file: UploadFile = File(...), admin: User = Depends(require_admin)
):
    """
    Uploads a text or markdown file to the RAG knowledge base.

    This endpoint accepts a UTF-8 encoded .txt or .md file, chunks its content,
    generates embeddings using Google's Gemini model, and stores the resulting
    vectors in the vector database for retrieval by the agent.

    Args:
        file (UploadFile): The file to upload. Must have a '.txt' or '.md'
            extension and be UTF-8 encoded.
        admin (User): The currently authenticated admin user, injected by the
            `require_admin` dependency.

    """

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(
            f"Rejected upload from admin='{admin.username}': "
            f"unsupported extension '{ext}' for file '{file.filename}'"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Only {sorted(ALLOWED_EXTENSIONS)} files are supported for now",
        )

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning(
            f"UTF-8 decode failed for file '{file.filename}' uploaded by admin='{admin.username}'"
        )
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")

    settings = get_settings()
    embedding_model = GoogleGenerativeAIEmbeddings(
        model=settings.GOOGLE_EMBEDDING_MODEL_NAME,
        api_key=settings.GOOGLE_API_KEY,
        output_dimensionality=settings.GOOGLE_EMBEDDING_MODEL_DIMS,
        # transport="rest",  # By default it uses GRPC but we need REST if we use proxy
    )

    chunks_stored = ingest_text(
        text=text, source_name=file.filename, embedding_model=embedding_model
    )

    return {
        "filename": file.filename,
        "uploaded_by": admin.username,
        "chunks_stored": chunks_stored,
    }
