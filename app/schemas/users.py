from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    favorite_team_id: str | None = None
    fan_points: int = 0
    accuracy_score: float = 1.0


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=80)
    favorite_team_id: str | None = Field(default=None, max_length=64)

