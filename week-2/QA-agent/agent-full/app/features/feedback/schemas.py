from pydantic import BaseModel
from typing import Literal


class FeedbackIn(BaseModel):
    thread_id: str
    message_id: str
    rating: Literal[-1, 1]  # +1 = like, -1 = dislike
    comment: str | None = None
