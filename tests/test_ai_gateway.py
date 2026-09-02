from app.repositories.store import InMemoryStore
from app.schemas.ai import (
    AICommentaryRequest,
    AICommentaryResponse,
    AIPreMatchPredictionLookupRequest,
    AIPredictionResponse,
)
from app.schemas.predictions import ProbabilityBreakdown
from app.services.ai_gateway import AIGateway


class CapturingAIClient:
    def __init__(self) -> None:
        self.commentary_request: AICommentaryRequest | None = None
        self.prediction_request: AIPreMatchPredictionLookupRequest | None = None

    def generate_commentary(self, payload: AICommentaryRequest) -> AICommentaryResponse:
        self.commentary_request = payload
        return AICommentaryResponse(
            request_id=payload.request_id,
            match_id=payload.match_id,
            event_id=payload.event_id,
            source_event_id=payload.source_event_id,
            sequence=payload.sequence,
            text="Captured commentary.",
            model_version="test",
            generated_at=payload.requested_at,
            safety={"passed": True, "flags": []},
        )

    def get_pre_match_prediction(self, payload: AIPreMatchPredictionLookupRequest) -> AIPredictionResponse:
        self.prediction_request = payload
        return AIPredictionResponse(
            request_id=payload.request_id,
            match_id=payload.match_id,
            probabilities=ProbabilityBreakdown(home=0.4, draw=0.3, away=0.3),
            confidence=0.5,
            insight_bullets=["Captured pre-match prediction."],
            model_version="test",
            generated_at=payload.requested_at,
        )


def test_commentary_request_includes_league_and_team_ids() -> None:
    client = CapturingAIClient()
    gateway = AIGateway(InMemoryStore(), client)

    gateway.generate_commentary_for_event("match-aur-har", "evt-3")

    assert client.commentary_request is not None
    request = client.commentary_request
    assert request.match_context.league_id == "demo-premier-league"
    assert request.match_context.home_team_id == "aurora-fc"
    assert request.match_context.away_team_id == "harbor-united"
    assert request.event.team_id == "aurora-fc"
    assert request.source_event_id == "api-football-demo-1003"
    assert request.occurred_at == "2026-08-04T21:21:00Z"


def test_prediction_request_is_pre_match_lookup_without_live_state() -> None:
    client = CapturingAIClient()
    gateway = AIGateway(InMemoryStore(), client)

    gateway.get_pre_match_prediction("match-aur-har")

    assert client.prediction_request is not None
    request = client.prediction_request
    payload = request.model_dump(mode="json")
    assert request.league_id == "demo-premier-league"
    assert request.home_team_id == "aurora-fc"
    assert request.away_team_id == "harbor-united"
    assert request.kickoff_at == "2026-08-04T20:00:00Z"
    assert "score" not in payload
    assert "minute" not in payload
    assert "timeline" not in payload
