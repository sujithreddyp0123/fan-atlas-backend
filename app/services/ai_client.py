from typing import Protocol

import httpx

from app.core.config import settings
from app.schemas.ai import (
    AIAudioPayload,
    AICommentaryRequest,
    AICommentaryResponse,
    AIPredictionRequest,
    AIPredictionResponse,
    AISafetyPayload,
)
from app.schemas.predictions import ProbabilityBreakdown


class AIClientError(RuntimeError):
    """Raised when an external AI service cannot return a valid response."""


class AIClient(Protocol):
    def generate_commentary(self, payload: AICommentaryRequest) -> AICommentaryResponse:
        raise NotImplementedError

    def predict_match(self, payload: AIPredictionRequest) -> AIPredictionResponse:
        raise NotImplementedError


class MockAIClient:
    """Zero-budget local AI client used until Antonio's service URLs are provided."""

    def generate_commentary(self, payload: AICommentaryRequest) -> AICommentaryResponse:
        event = payload.event
        if event.type in {"substitution", "var_check"}:
            status = "no_line"
            text = ""
        else:
            status = "available"
            team = event.team_name or "the team"
            text = f"{team} has a key {event.type} moment at minute {event.minute}."
        return AICommentaryResponse(
            request_id=payload.request_id,
            match_id=payload.match_id,
            event_id=payload.event_id,
            source_event_id=payload.source_event_id,
            sequence=payload.sequence,
            status=status,
            language_code=payload.language_code,
            text=text,
            audio=AIAudioPayload(status="not_generated"),
            model_version="mock-commentary-v1",
            generated_at=payload.requested_at,
            safety=AISafetyPayload(passed=True),
        )

    def predict_match(self, payload: AIPredictionRequest) -> AIPredictionResponse:
        score = payload.match.score
        if score.home > score.away:
            probabilities = ProbabilityBreakdown(home=0.58, draw=0.24, away=0.18)
        elif score.away > score.home:
            probabilities = ProbabilityBreakdown(home=0.22, draw=0.25, away=0.53)
        else:
            probabilities = ProbabilityBreakdown(home=0.41, draw=0.31, away=0.28)
        return AIPredictionResponse(
            request_id=payload.request_id,
            match_id=payload.match_id,
            probabilities=probabilities,
            confidence=0.62,
            insight_bullets=[
                "Mock prediction generated from current match state.",
                "Replace this client with Antonio's AI endpoint when ready.",
            ],
            model_version="mock-prediction-v1",
            generated_at=payload.requested_at,
        )


class HttpAIClient:
    """HTTP client for Antonio's commentary and prediction services."""

    def __init__(
        self,
        commentary_url: str,
        prediction_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 2.5,
    ) -> None:
        self.commentary_url = commentary_url
        self.prediction_url = prediction_url
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def generate_commentary(self, payload: AICommentaryRequest) -> AICommentaryResponse:
        if not self.commentary_url:
            raise AIClientError("AI commentary URL is not configured")
        try:
            response = httpx.post(
                self.commentary_url,
                json=payload.model_dump(mode="json"),
                headers=self._headers(),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return AICommentaryResponse.model_validate(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise AIClientError(f"AI commentary request failed: {type(exc).__name__}") from exc

    def predict_match(self, payload: AIPredictionRequest) -> AIPredictionResponse:
        if not self.prediction_url:
            raise AIClientError("AI prediction URL is not configured")
        try:
            response = httpx.post(
                self.prediction_url,
                json=payload.model_dump(mode="json"),
                headers=self._headers(),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return AIPredictionResponse.model_validate(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise AIClientError(f"AI prediction request failed: {type(exc).__name__}") from exc


def get_ai_client() -> AIClient:
    if settings.ai_client_mode == "http":
        return HttpAIClient(
            commentary_url=settings.ai_commentary_url,
            prediction_url=settings.ai_prediction_url,
            api_key=settings.ai_api_key or None,
            timeout_seconds=settings.ai_timeout_seconds,
        )
    return MockAIClient()

