# FanAtlas Frontend API Contract

This document is the first shared contract for mobile, web, and future clients.

## Base URLs

| Environment | Base URL |
| --- | --- |
| Local | `http://127.0.0.1:8000` |
| Local API v1 | `http://127.0.0.1:8000/api/v1` |

## Headers

| Header | Direction | Purpose |
| --- | --- | --- |
| `Authorization: Bearer <token>` | Client to API | Authenticated endpoints |
| `X-Request-ID` | Optional client to API | Correlate frontend logs with backend logs |
| `X-Request-ID` | API to client | Returned on every HTTP response |

## Standard Error Shape

All handled API errors use the same shape:

```json
{
  "error": {
    "code": "not_found",
    "message": "Match not found",
    "request_id": "req-abc123",
    "details": []
  }
}
```

`details` is present only when useful, such as validation errors.

## Auth Flow

1. Client calls `POST /api/v1/auth/login`.
2. API returns `access_token`.
3. Client stores the token in secure storage.
4. Client sends `Authorization: Bearer <token>` for protected endpoints.
5. Client calls `POST /api/v1/auth/refresh` before treating a session as expired.

## Screen-to-Endpoint Map

| Screen | Endpoint |
| --- | --- |
| Home | `GET /api/v1/matches?status=live` and `GET /api/v1/leaderboard` |
| Games | `GET /api/v1/matches?status=<status>&league=<league>&date=<yyyy-mm-dd>` |
| Match Detail | `GET /api/v1/matches/{match_id}/center` |
| Live Match | `GET /api/v1/matches/{match_id}/center` plus `WS /api/v1/ws/matches/{match_id}` |
| Predict | `GET /api/v1/matches/{match_id}/predictions`, `GET /api/v1/matches/{match_id}/community-prediction`, `POST /api/v1/predictions` |
| Insights | `GET /api/v1/matches/{match_id}/insights` |
| Profile | `GET /api/v1/me`, `PATCH /api/v1/me/profile` |
| Feedback | `POST /api/v1/feedback` |

## Realtime Messages

Every WebSocket message uses:

```json
{
  "type": "match.snapshot",
  "match_id": "match-aur-har",
  "sequence": 0,
  "payload": {}
}
```

Known MVP message types:

| Type | Purpose |
| --- | --- |
| `match.snapshot` | Initial state after connect |
| `match.clock` | Current live minute/status |
| `commentary.available` | Commentary/audio item is ready |
| `pong` | Response to client ping |
| `error` | Unsupported message or recoverable realtime error |

## OpenAPI

Runtime OpenAPI JSON:

```text
GET /openapi.json
```

Export a checked-in contract locally:

```powershell
.venv\Scripts\python.exe scripts\export_openapi.py
```

