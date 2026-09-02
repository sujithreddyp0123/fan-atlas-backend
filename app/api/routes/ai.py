from fastapi import APIRouter, HTTPException, status

from app.repositories.store import get_store
from app.schemas.ai import AICommentaryResponse, AIPredictionResponse
from app.services.ai_client import AIClientError
from app.services.ai_gateway import AIGateway

router = APIRouter()


@router.post("/commentary/matches/{match_id}/events/{event_id}", response_model=AICommentaryResponse)
def generate_commentary(match_id: str, event_id: str) -> AICommentaryResponse:
    try:
        return AIGateway(get_store()).generate_commentary_for_event(match_id, event_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc).strip("'")) from exc
    except AIClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/predictions/matches/{match_id}", response_model=AIPredictionResponse)
def generate_prediction(match_id: str) -> AIPredictionResponse:
    try:
        return AIGateway(get_store()).get_pre_match_prediction(match_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc).strip("'")) from exc
    except AIClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
