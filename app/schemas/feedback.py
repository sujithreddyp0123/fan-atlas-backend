from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    category: str = Field(min_length=2, max_length=60)
    message: str = Field(min_length=3, max_length=1000)
    match_id: str | None = None


class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    category: str
    message: str
    match_id: str | None = None
    status: str = "received"

