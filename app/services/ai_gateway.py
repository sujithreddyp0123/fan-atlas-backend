from datetime import datetime, timezone
from uuid import uuid4

from app.repositories.store import InMemoryStore
from app.schemas.ai import (
    AICommentaryRequest,
    AIEventPayload,
    AIMatchContext,
    AIPredictionMatchPayload,
    AIPredictionRequest,
    AIPredictionTimelineItem,
)
from app.services.ai_client import AIClient, get_ai_client


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class AIGateway:
    def __init__(self, store: InMemoryStore, client: AIClient | None = None) -> None:
        self.store = store
        self.client = client or get_ai_client()

    def generate_commentary_for_event(self, match_id: str, event_id: str):
        match = self.store.get_match_detail(match_id)
        if not match:
            raise KeyError("Match not found")
        event = next((item for item in match.timeline if item.id == event_id), None)
        if not event:
            raise KeyError("Event not found")
        team_name = None
        if event.team_id == match.home_team.id:
            team_name = match.home_team.name
        elif event.team_id == match.away_team.id:
            team_name = match.away_team.name
        request = AICommentaryRequest(
            request_id="ai-comm-" + uuid4().hex[:12],
            requested_at=utc_now_iso(),
            match_id=match.id,
            event_id=event.id,
            source_event_id=event.source_event_id,
            sequence=event.sequence,
            occurred_at=event.occurred_at,
            language_code="en",
            event=AIEventPayload(
                type=event.type,
                minute=event.minute,
                team_id=event.team_id,
                team_name=team_name,
                player_name=event.player_name,
                score=event.score,
                text=event.text,
            ),
            match_context=AIMatchContext(
                league=match.league,
                home_team=match.home_team.name,
                away_team=match.away_team.name,
                status=match.status.value,
            ),
        )
        return self.client.generate_commentary(request)

    def predict_match(self, match_id: str):
        match = self.store.get_match_detail(match_id)
        if not match:
            raise KeyError("Match not found")
        request = AIPredictionRequest(
            request_id="ai-pred-" + uuid4().hex[:12],
            requested_at=utc_now_iso(),
            match_id=match.id,
            match=AIPredictionMatchPayload(
                league=match.league,
                home_team=match.home_team.name,
                away_team=match.away_team.name,
                status=match.status.value,
                minute=match.minute,
                score=match.score,
            ),
            timeline=[
                AIPredictionTimelineItem(
                    minute=event.minute,
                    type=event.type,
                    team_id=event.team_id,
                    source_event_id=event.source_event_id,
                    occurred_at=event.occurred_at,
                )
                for event in match.timeline
            ],
        )
        return self.client.predict_match(request)

