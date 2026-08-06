from fastapi import APIRouter, HTTPException, Query, status

from app.repositories.store import get_store
from app.schemas.matches import (
    CommentaryResponse,
    InsightsResponse,
    MatchCenter,
    MatchDetail,
    MatchListResponse,
    MatchStatus,
    TimelineResponse,
)

router = APIRouter()


@router.get("", response_model=MatchListResponse)
def list_matches(
    league: str | None = Query(default=None),
    status_filter: MatchStatus | None = Query(default=None, alias="status"),
    date: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> MatchListResponse:
    return get_store().list_matches(league=league, status=status_filter, date=date, page=page, page_size=page_size)


@router.get("/{match_id}", response_model=MatchDetail)
def get_match(match_id: str) -> MatchDetail:
    match = get_store().get_match_detail(match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.get("/{match_id}/center", response_model=MatchCenter)
def get_match_center(match_id: str) -> MatchCenter:
    center = get_store().get_match_center(match_id)
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return center


@router.get("/{match_id}/timeline", response_model=TimelineResponse)
def get_timeline(match_id: str) -> TimelineResponse:
    timeline = get_store().get_timeline(match_id)
    if timeline is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return timeline


@router.get("/{match_id}/commentary", response_model=CommentaryResponse)
def get_commentary(match_id: str) -> CommentaryResponse:
    commentary = get_store().get_commentary(match_id)
    if commentary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return commentary


@router.get("/{match_id}/insights", response_model=InsightsResponse)
def get_insights(match_id: str) -> InsightsResponse:
    insights = get_store().get_insights(match_id)
    if insights is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return insights

