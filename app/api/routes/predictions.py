from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.repositories.store import get_store
from app.schemas.predictions import (
    CommunityPrediction,
    MatchPredictionResponse,
    PredictionSubmissionRequest,
    PredictionSubmissionResponse,
)
from app.schemas.users import UserPublic

router = APIRouter()


@router.get("/matches/{match_id}/predictions", response_model=MatchPredictionResponse)
def get_match_predictions(match_id: str) -> MatchPredictionResponse:
    prediction = get_store().get_match_predictions(match_id)
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return prediction


@router.get("/matches/{match_id}/community-prediction", response_model=CommunityPrediction)
def get_community_prediction(match_id: str) -> CommunityPrediction:
    prediction = get_store().get_community_prediction(match_id)
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return prediction


@router.post("/predictions", response_model=PredictionSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_prediction(
    payload: PredictionSubmissionRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> PredictionSubmissionResponse:
    try:
        return get_store().submit_prediction(current_user.id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

