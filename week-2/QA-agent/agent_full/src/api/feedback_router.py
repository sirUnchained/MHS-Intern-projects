from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth.deps import get_db, get_current_user
from src.auth.models import User
from src.database.models import Feedback

router = APIRouter(prefix="/chat", tags=["feedback"])


class FeedbackIn(BaseModel):
    thread_id: str
    message_id: str
    rating: Literal[-1, 1]  # +1 = like, -1 = dislike
    comment: str | None = None


@router.post(
    "/feedback",
    summary="Submit like/dislike feedback on an assistant message",
    description=(
        "Records a +1 (like) or -1 (dislike) rating for a specific assistant "
        "message, keyed by thread_id + message_id. Requires an authenticated "
        "user (JWT)."
    ),
)
def submit_feedback(
    payload: FeedbackIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    fb = Feedback(
        user_id=str(user.id),
        thread_id=payload.thread_id,
        message_id=payload.message_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"status": "ok", "feedback_id": fb.id}
