from enum import StrEnum

from pydantic import BaseModel


class LeaderboardScope(StrEnum):
    global_ = "global"
    friends = "friends"
    top_predictors = "top_predictors"


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    display_name: str
    fan_points: int
    accuracy_score: float


class LeaderboardResponse(BaseModel):
    scope: LeaderboardScope
    items: list[LeaderboardEntry]

