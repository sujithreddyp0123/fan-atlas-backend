from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str


class VersionResponse(BaseModel):
    name: str
    version: str


class MessageResponse(BaseModel):
    message: str


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    has_next: bool

