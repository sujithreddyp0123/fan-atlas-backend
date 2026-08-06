from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.repositories.store import get_store
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.schemas.users import UserPublic

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> FeedbackResponse:
    return get_store().create_feedback(current_user.id, payload)

