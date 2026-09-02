# FanAtlas AI Layer Compatibility Contract

This document defines the boundary between the FanAtlas universal backend and Antonio's AI layers.

The backend can run without AI services using seeded/mock outputs. When Antonio's services are ready, the backend should call them through these contracts.

## Ownership Boundary

| Area | Owner |
| --- | --- |
| Commentary intelligence, prompt strategy, multilingual generation, voice generation | Antonio AI layer |
| Prediction model, probabilities, insights, model evaluation | Antonio AI layer |
| Authenticated user APIs, match data, storage, replay, delivery to mobile/web | FanAtlas backend |
| Caching, history, rewind, Match Center aggregation, WebSocket delivery | FanAtlas backend |

## Commentary Generation Request

Backend sends one validated match event at a time.

```json
{
  "request_id": "req-123",
  "match_id": "match-aur-har",
  "event_id": "evt-3",
  "source_event_id": "api-football-demo-1003",
  "sequence": 3,
  "occurred_at": "2026-08-04T21:21:00Z",
  "language_code": "en",
  "voice_profile_id": "text_only",
  "event": {
    "type": "goal",
    "minute": 61,
    "team_id": "aurora-fc",
    "team_name": "Aurora FC",
    "player_name": "Nico Vale",
    "score": {
      "home": 2,
      "away": 1
    },
    "text": "Nico Vale restores Aurora's lead."
  },
  "match_context": {
    "league_id": "demo-premier-league",
    "league": "Demo Premier League",
    "home_team_id": "aurora-fc",
    "home_team": "Aurora FC",
    "away_team_id": "harbor-united",
    "away_team": "Harbor United",
    "status": "live"
  }
}
```

## Commentary Generation Response

```json
{
  "request_id": "req-123",
  "match_id": "match-aur-har",
  "event_id": "evt-3",
  "source_event_id": "api-football-demo-1003",
  "sequence": 3,
  "status": "available",
  "duplicate_of_event_id": null,
  "language_code": "en",
  "text": "Nico Vale pounces, Aurora leads 2-1, and the tempo jumps again.",
  "audio": {
    "status": "not_generated",
    "url": null,
    "duration_ms": null,
    "waveform": []
  },
  "model_version": "commentary-v1",
  "generated_at": "2026-08-04T20:15:00Z",
  "safety": {
    "passed": true,
    "flags": []
  }
}
```

## Pre-Match Prediction Lookup Request

The backend does not ask the Prediction Engine to recalculate from live match
state. It looks up or requests the pre-calculated prediction created before
kickoff.

```json
{
  "request_id": "req-456",
  "requested_at": "2026-08-04T18:00:00Z",
  "match_id": "match-aur-har",
  "market": "match_result",
  "language_code": "en",
  "league_id": "demo-premier-league",
  "league": "Demo Premier League",
  "home_team_id": "aurora-fc",
  "home_team": "Aurora FC",
  "away_team_id": "harbor-united",
  "away_team": "Harbor United",
  "kickoff_at": "2026-08-04T20:00:00Z"
}
```

## Match Prediction Response

```json
{
  "request_id": "req-456",
  "match_id": "match-aur-har",
  "market": "match_result",
  "probabilities": {
    "home": 0.58,
    "draw": 0.24,
    "away": 0.18
  },
  "confidence": 0.64,
  "insight_bullets": [
    "Aurora is creating more shots on target.",
    "Harbor remains dangerous on transitions."
  ],
  "model_version": "prediction-v1",
  "generated_at": "2026-08-04T20:15:00Z"
}
```

## Backend Expectations

- AI services should use HTTPS in non-local environments.
- AI services should return JSON only.
- AI services should not require direct mobile/web access.
- Backend will own retries, caching, persistence, and delivery.
- Backend expects timeouts to be safe for a live UI, ideally under 2.5 seconds for text.
- If AI service fails, backend will return seeded/mock fallback for MVP.
- Prediction lookup should use the pre-match prediction keyed by `match_id`
  and stable league/team identifiers, not live score, minute, or timeline.

## Duplicate And No-Line Cases

Commentary responses use `status` to represent non-standard outcomes.

| Status | Meaning |
| --- | --- |
| `available` | Commentary text is ready and can be shown/played |
| `duplicate` | Event is a duplicate and should map to `duplicate_of_event_id` |
| `no_line` | Valid event, but no commentary line should be shown |
| `fallback` | Backend or AI fallback generated a safe line |
| `failed` | AI could not produce a usable line |

`source_event_id` should remain stable for the provider event. Backend will use it as the dedupe key when available.

`occurred_at` should represent the actual event timestamp from provider/live data. If the provider does not supply an absolute timestamp, backend may send `null` and rely on `minute` plus `sequence`.

## Open Questions For Antonio

| Question | Needed Decision |
| --- | --- |
| Hosting | Will Antonio host the AI services, or should this backend deploy them? |
| Auth | Shared API key, JWT, mTLS, or internal network only? |
| Audio | Will commentary service return audio URL, audio bytes, or text only at MVP? |
| Languages | Which languages are actually supported in MVP? |
| Latency | Target p95 latency for commentary and predictions? |
| Versioning | How should model/prompt versions be exposed? |
| Fallback | Should backend fallback be deterministic templates or Antonio-provided fallback text? |
