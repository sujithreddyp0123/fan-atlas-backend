from __future__ import annotations

from math import ceil
from uuid import uuid4

from app.core.security import hash_password, verify_password
from app.schemas.common import Pagination
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse, LeaderboardScope
from app.schemas.matches import (
    CommentaryItem,
    CommentaryResponse,
    InsightsResponse,
    MatchCenter,
    MatchDetail,
    MatchListResponse,
    MatchStats,
    MatchStatus,
    MatchSummary,
    ScoreState,
    TeamSummary,
    TimelineEvent,
    TimelineResponse,
)
from app.schemas.predictions import (
    CommunityPrediction,
    MatchPredictionResponse,
    PredictionSubmissionRequest,
    PredictionSubmissionResponse,
    ProbabilityBreakdown,
)
from app.schemas.users import UpdateProfileRequest, UserPublic


class InMemoryStore:
    def __init__(self) -> None:
        self._password_hashes: dict[str, str] = {}
        self.users: dict[str, UserPublic] = {}
        self.matches: dict[str, MatchDetail] = {}
        self.commentary: dict[str, list[CommentaryItem]] = {}
        self.ai_predictions: dict[str, MatchPredictionResponse] = {}
        self.prediction_submissions: list[PredictionSubmissionResponse] = []
        self.feedback: list[FeedbackResponse] = []
        self._seed()

    def _seed(self) -> None:
        demo = self.create_user("demo@fanatlas.app", "password123", "Demo Fan")
        self.users["user-rina"] = UserPublic(
            id="user-rina",
            email="rina@example.com",
            display_name="Rina",
            favorite_team_id="aurora-fc",
            fan_points=920,
            accuracy_score=0.74,
        )
        self.users["user-malik"] = UserPublic(
            id="user-malik",
            email="malik@example.com",
            display_name="Malik",
            favorite_team_id="harbor-united",
            fan_points=875,
            accuracy_score=0.68,
        )
        self.users[demo.id] = demo.model_copy(update={"favorite_team_id": "aurora-fc", "fan_points": 640})

        aurora = TeamSummary(id="aurora-fc", name="Aurora FC", abbreviation="AUR")
        harbor = TeamSummary(id="harbor-united", name="Harbor United", abbreviation="HAR")
        metro = TeamSummary(id="metro-city", name="Metro City", abbreviation="MET")
        riverside = TeamSummary(id="riverside-club", name="Riverside Club", abbreviation="RIV")

        self.matches["match-aur-har"] = MatchDetail(
            id="match-aur-har",
            league="Demo Premier League",
            kickoff_at="2026-08-04T20:00:00Z",
            status=MatchStatus.live,
            minute=64,
            home_team=aurora,
            away_team=harbor,
            score=ScoreState(home=2, away=1),
            venue="Atlas Park",
            stats=MatchStats(
                possession_home=55,
                possession_away=45,
                shots_home=12,
                shots_away=8,
                shots_on_target_home=6,
                shots_on_target_away=3,
            ),
            timeline=[
                TimelineEvent(
                    id="evt-1",
                    source_event_id="api-football-demo-1001",
                    sequence=1,
                    minute=12,
                    occurred_at="2026-08-04T20:12:00Z",
                    type="goal",
                    team_id="aurora-fc",
                    player_name="Kai Morgan",
                    text="Kai Morgan opens the scoring for Aurora FC.",
                    score=ScoreState(home=1, away=0),
                ),
                TimelineEvent(
                    id="evt-2",
                    source_event_id="api-football-demo-1002",
                    sequence=2,
                    minute=38,
                    occurred_at="2026-08-04T20:38:00Z",
                    type="goal",
                    team_id="harbor-united",
                    player_name="Leo Santos",
                    text="Leo Santos levels it before halftime.",
                    score=ScoreState(home=1, away=1),
                ),
                TimelineEvent(
                    id="evt-3",
                    source_event_id="api-football-demo-1003",
                    sequence=3,
                    minute=61,
                    occurred_at="2026-08-04T21:21:00Z",
                    type="goal",
                    team_id="aurora-fc",
                    player_name="Nico Vale",
                    text="Nico Vale restores Aurora's lead.",
                    score=ScoreState(home=2, away=1),
                ),
            ],
        )
        self.matches["match-met-riv"] = MatchDetail(
            id="match-met-riv",
            league="Demo Premier League",
            kickoff_at="2026-08-05T18:30:00Z",
            status=MatchStatus.upcoming,
            minute=None,
            home_team=metro,
            away_team=riverside,
            score=ScoreState(home=0, away=0),
            venue="Metro Ground",
            stats=MatchStats(
                possession_home=0,
                possession_away=0,
                shots_home=0,
                shots_away=0,
                shots_on_target_home=0,
                shots_on_target_away=0,
            ),
            timeline=[],
        )

        self.commentary["match-aur-har"] = [
            CommentaryItem(
                id="cm-1",
                sequence=1,
                timeline_event_id="evt-1",
                source_event_id="api-football-demo-1001",
                text="Aurora strikes first, and the home crowd has lift-off.",
                starts_at_ms=0,
                duration_ms=4200,
            ),
            CommentaryItem(
                id="cm-2",
                sequence=2,
                timeline_event_id="evt-2",
                source_event_id="api-football-demo-1002",
                text="Harbor answers with a composed finish, and this match is level again.",
                starts_at_ms=4200,
                duration_ms=5100,
            ),
            CommentaryItem(
                id="cm-3",
                sequence=3,
                timeline_event_id="evt-3",
                source_event_id="api-football-demo-1003",
                text="Nico Vale pounces, Aurora leads 2-1, and the tempo jumps again.",
                starts_at_ms=9300,
                duration_ms=5300,
            ),
        ]
        self.commentary["match-met-riv"] = []

        self.ai_predictions["match-aur-har"] = MatchPredictionResponse(
            match_id="match-aur-har",
            probabilities=ProbabilityBreakdown(home=0.58, draw=0.24, away=0.18),
            confidence=0.64,
            insight_bullets=[
                "Aurora is creating more shots on target.",
                "Harbor remains dangerous on transitions.",
                "The next goal likely decides the match state.",
            ],
        )
        self.ai_predictions["match-met-riv"] = MatchPredictionResponse(
            match_id="match-met-riv",
            probabilities=ProbabilityBreakdown(home=0.41, draw=0.31, away=0.28),
            confidence=0.52,
            insight_bullets=[
                "Metro has the stronger recent home form.",
                "Riverside has conceded fewer late goals.",
            ],
        )

    def create_user(self, email: str, password: str, display_name: str) -> UserPublic:
        user = UserPublic(
            id="user-" + uuid4().hex[:10],
            email=email,
            display_name=display_name,
            favorite_team_id=None,
            fan_points=0,
            accuracy_score=1.0,
        )
        self.users[user.id] = user
        self._password_hashes[user.id] = hash_password(password)
        return user

    def get_user_by_email(self, email: str) -> UserPublic | None:
        normalized = email.lower()
        return next((user for user in self.users.values() if user.email.lower() == normalized), None)

    def get_user_by_id(self, user_id: str) -> UserPublic | None:
        return self.users.get(user_id)

    def authenticate_user(self, email: str, password: str) -> UserPublic | None:
        user = self.get_user_by_email(email)
        if not user:
            return None
        password_hash = self._password_hashes.get(user.id)
        if not password_hash or not verify_password(password, password_hash):
            return None
        return user

    def update_user_profile(self, user_id: str, payload: UpdateProfileRequest) -> UserPublic:
        user = self.users[user_id]
        updates = payload.model_dump(exclude_unset=True)
        updated = user.model_copy(update=updates)
        self.users[user_id] = updated
        return updated

    def list_matches(
        self,
        league: str | None,
        status: MatchStatus | None,
        date: str | None,
        page: int,
        page_size: int,
    ) -> MatchListResponse:
        items: list[MatchSummary] = list(self.matches.values())
        if league:
            items = [match for match in items if match.league.lower() == league.lower()]
        if status:
            items = [match for match in items if match.status == status]
        if date:
            items = [match for match in items if match.kickoff_at.startswith(date)]
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return MatchListResponse(
            items=items[start:end],
            pagination=Pagination(
                page=page,
                page_size=page_size,
                total=total,
                has_next=page < ceil(total / page_size) if total else False,
            ),
        )

    def get_match_detail(self, match_id: str) -> MatchDetail | None:
        return self.matches.get(match_id)

    def get_timeline(self, match_id: str) -> TimelineResponse | None:
        match = self.matches.get(match_id)
        if not match:
            return None
        return TimelineResponse(match_id=match_id, items=match.timeline)

    def get_commentary(self, match_id: str) -> CommentaryResponse | None:
        if match_id not in self.matches:
            return None
        return CommentaryResponse(match_id=match_id, items=self.commentary.get(match_id, []))

    def get_match_predictions(self, match_id: str) -> MatchPredictionResponse | None:
        if match_id not in self.matches:
            return None
        return self.ai_predictions[match_id]

    def get_community_prediction(self, match_id: str) -> CommunityPrediction | None:
        if match_id not in self.matches:
            return None
        submissions = [item for item in self.prediction_submissions if item.match_id == match_id]
        if not submissions:
            return CommunityPrediction(
                match_id=match_id,
                total_predictions=0,
                weighted_percentages=ProbabilityBreakdown(home=0.0, draw=0.0, away=0.0),
                method="no_submissions_yet",
            )
        weights = {"home": 0.0, "draw": 0.0, "away": 0.0}
        total_weight = 0.0
        for item in submissions:
            user = self.users[item.user_id]
            weight = max(user.accuracy_score, 0.1)
            weights[item.choice.value] += weight
            total_weight += weight
        return CommunityPrediction(
            match_id=match_id,
            total_predictions=len(submissions),
            weighted_percentages=ProbabilityBreakdown(
                home=round(weights["home"] / total_weight, 4),
                draw=round(weights["draw"] / total_weight, 4),
                away=round(weights["away"] / total_weight, 4),
            ),
            method="accuracy_weighted_mvp",
        )

    def get_insights(self, match_id: str) -> InsightsResponse | None:
        match = self.matches.get(match_id)
        if not match:
            return None
        prediction = self.ai_predictions[match_id]
        return InsightsResponse(
            match_id=match_id,
            bullets=prediction.insight_bullets,
            team_form={
                match.home_team.id: ["W", "W", "D", "L", "W"],
                match.away_team.id: ["D", "L", "W", "D", "W"],
            },
        )

    def get_match_center(self, match_id: str) -> MatchCenter | None:
        match = self.matches.get(match_id)
        if not match:
            return None
        return MatchCenter(
            match=match,
            commentary=self.commentary.get(match_id, []),
            ai_prediction=self.ai_predictions[match_id],
            community_prediction=self.get_community_prediction(match_id),
            insights=self.get_insights(match_id),
        )

    def get_live_snapshot(self, match_id: str) -> dict | None:
        center = self.get_match_center(match_id)
        if not center:
            return None
        return {
            "match": center.match.model_dump(mode="json"),
            "timeline": [item.model_dump(mode="json") for item in center.match.timeline],
            "commentary": [item.model_dump(mode="json") for item in center.commentary],
            "stream_status": center.stream_status,
        }

    def get_seeded_live_events(self, match_id: str) -> list[dict]:
        if match_id != "match-aur-har":
            return []
        return [
            {
                "type": "match.clock",
                "payload": {"minute": 65, "status": "live"},
            },
            {
                "type": "commentary.available",
                "payload": {
                    "commentary_id": "cm-3",
                    "timeline_event_id": "evt-3",
                    "audio_status": "text_only",
                },
            },
        ]

    def submit_prediction(self, user_id: str, payload: PredictionSubmissionRequest) -> PredictionSubmissionResponse:
        match = self.matches.get(payload.match_id)
        if not match:
            raise KeyError("Match not found")
        if match.status != MatchStatus.upcoming:
            raise ValueError("Predictions are locked for this match")
        submission = PredictionSubmissionResponse(
            id="pred-" + uuid4().hex[:10],
            match_id=payload.match_id,
            user_id=user_id,
            market=payload.market,
            choice=payload.choice,
            locked=False,
            awarded_points=0,
        )
        self.prediction_submissions.append(submission)
        return submission

    def get_leaderboard(self, scope: LeaderboardScope) -> LeaderboardResponse:
        ranked = sorted(self.users.values(), key=lambda user: user.fan_points, reverse=True)
        return LeaderboardResponse(
            scope=scope,
            items=[
                LeaderboardEntry(
                    rank=index,
                    user_id=user.id,
                    display_name=user.display_name,
                    fan_points=user.fan_points,
                    accuracy_score=user.accuracy_score,
                )
                for index, user in enumerate(ranked, start=1)
            ],
        )

    def create_feedback(self, user_id: str, payload: FeedbackRequest) -> FeedbackResponse:
        feedback = FeedbackResponse(id="fb-" + uuid4().hex[:10], user_id=user_id, **payload.model_dump())
        self.feedback.append(feedback)
        return feedback


store = InMemoryStore()


def get_store() -> InMemoryStore:
    return store
