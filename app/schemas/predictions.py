from enum import StrEnum

from pydantic import BaseModel, Field


class PredictionChoice(StrEnum):
    home = "home"
    draw = "draw"
    away = "away"


class ProbabilityBreakdown(BaseModel):
    home: float = Field(ge=0, le=1)
    draw: float = Field(ge=0, le=1)
    away: float = Field(ge=0, le=1)


class MatchPredictionResponse(BaseModel):
    match_id: str
    market: str = "match_result"
    probabilities: ProbabilityBreakdown
    confidence: float = Field(ge=0, le=1)
    insight_bullets: list[str]
    model_version: str = "mock-v1"
    generated_by: str = "mock"


class CommunityPrediction(BaseModel):
    match_id: str
    market: str = "match_result"
    total_predictions: int
    weighted_percentages: ProbabilityBreakdown
    method: str


class PredictionSubmissionRequest(BaseModel):
    match_id: str
    market: str = "match_result"
    choice: PredictionChoice


class PredictionSubmissionResponse(BaseModel):
    id: str
    match_id: str
    user_id: str
    market: str
    choice: PredictionChoice
    locked: bool
    awarded_points: int

