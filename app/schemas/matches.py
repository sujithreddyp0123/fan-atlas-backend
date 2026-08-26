from enum import StrEnum

from pydantic import BaseModel

from app.schemas.common import Pagination
from app.schemas.predictions import CommunityPrediction, MatchPredictionResponse


class MatchStatus(StrEnum):
    upcoming = "upcoming"
    live = "live"
    halftime = "halftime"
    completed = "completed"
    postponed = "postponed"


class TeamSummary(BaseModel):
    id: str
    name: str
    abbreviation: str
    logo_url: str | None = None


class ScoreState(BaseModel):
    home: int
    away: int


class MatchSummary(BaseModel):
    id: str
    league: str
    kickoff_at: str
    status: MatchStatus
    minute: int | None = None
    home_team: TeamSummary
    away_team: TeamSummary
    score: ScoreState
    venue: str | None = None


class MatchStats(BaseModel):
    possession_home: int
    possession_away: int
    shots_home: int
    shots_away: int
    shots_on_target_home: int
    shots_on_target_away: int


class TimelineEvent(BaseModel):
    id: str
    source_event_id: str
    sequence: int
    minute: int
    occurred_at: str | None = None
    type: str
    team_id: str | None = None
    player_name: str | None = None
    text: str
    score: ScoreState


class CommentaryItem(BaseModel):
    id: str
    sequence: int
    timeline_event_id: str
    source_event_id: str
    status: str = "available"
    text: str
    language_code: str = "en"
    audio_url: str | None = None
    starts_at_ms: int | None = None
    duration_ms: int | None = None
    generated_by: str = "mock"


class MatchDetail(MatchSummary):
    stats: MatchStats
    timeline: list[TimelineEvent]


class MatchListResponse(BaseModel):
    items: list[MatchSummary]
    pagination: Pagination


class TimelineResponse(BaseModel):
    match_id: str
    items: list[TimelineEvent]


class CommentaryResponse(BaseModel):
    match_id: str
    items: list[CommentaryItem]


class InsightsResponse(BaseModel):
    match_id: str
    bullets: list[str]
    team_form: dict[str, list[str]]
    generated_by: str = "seeded"


class MatchCenter(BaseModel):
    match: MatchDetail
    commentary: list[CommentaryItem]
    ai_prediction: MatchPredictionResponse
    community_prediction: CommunityPrediction
    insights: InsightsResponse
    stream_status: str = "available"
