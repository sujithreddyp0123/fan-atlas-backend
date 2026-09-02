from pydantic import BaseModel, Field

from app.schemas.matches import ScoreState
from app.schemas.predictions import ProbabilityBreakdown


class AIEventPayload(BaseModel):
    type: str
    minute: int | None = None
    team_id: str | None = None
    team_name: str | None = None
    player_name: str | None = None
    score: ScoreState
    text: str


class AIMatchContext(BaseModel):
    league_id: str
    league: str
    home_team_id: str
    home_team: str
    away_team_id: str
    away_team: str
    status: str


class AICommentaryRequest(BaseModel):
    request_id: str
    requested_at: str
    match_id: str
    event_id: str
    source_event_id: str
    sequence: int
    occurred_at: str | None = None
    language_code: str = "en"
    voice_profile_id: str = "text_only"
    event: AIEventPayload
    match_context: AIMatchContext


class AIAudioPayload(BaseModel):
    status: str = "not_generated"
    url: str | None = None
    duration_ms: int | None = None
    waveform: list[float] = Field(default_factory=list)


class AISafetyPayload(BaseModel):
    passed: bool
    flags: list[str] = Field(default_factory=list)


class AICommentaryResponse(BaseModel):
    request_id: str
    match_id: str
    event_id: str
    source_event_id: str
    sequence: int
    status: str = "available"
    duplicate_of_event_id: str | None = None
    language_code: str = "en"
    text: str
    audio: AIAudioPayload = Field(default_factory=AIAudioPayload)
    model_version: str
    generated_at: str
    safety: AISafetyPayload


class AIPreMatchPredictionLookupRequest(BaseModel):
    request_id: str
    requested_at: str
    match_id: str
    market: str = "match_result"
    language_code: str = "en"
    league_id: str
    league: str
    home_team_id: str
    home_team: str
    away_team_id: str
    away_team: str
    kickoff_at: str


class AIPredictionResponse(BaseModel):
    request_id: str
    match_id: str
    market: str = "match_result"
    probabilities: ProbabilityBreakdown
    confidence: float = Field(ge=0, le=1)
    insight_bullets: list[str]
    model_version: str
    generated_at: str
