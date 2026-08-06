from fastapi import APIRouter, Query

from app.repositories.store import get_store
from app.schemas.leaderboard import LeaderboardResponse, LeaderboardScope

router = APIRouter()


@router.get("", response_model=LeaderboardResponse)
def get_leaderboard(
    scope: LeaderboardScope = Query(default=LeaderboardScope.global_),
) -> LeaderboardResponse:
    return get_store().get_leaderboard(scope)

