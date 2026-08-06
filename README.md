# FanAtlas Universal Backend

Zero-budget MVP backend for FanAtlas. This is a universal API intended to serve mobile, web, and future clients from the same stable contract.

## MVP Principles

- One backend API, many clients.
- Seeded/mock data first so frontend can integrate immediately.
- Free football APIs can be added behind adapters later.
- Paid APIs, AWS, Redis, CDN, and production infra are post-MVP unless approved.
- Antonio's AI commentary and prediction services are integration boundaries; this backend can run with mocks until those contracts are ready.

## What Is Included

- Auth endpoints with demo JWT flow.
- User profile endpoint.
- Match list and match detail endpoints.
- Match Center aggregate endpoint.
- Timeline and commentary endpoints.
- Prediction submission and community prediction endpoints.
- Leaderboard and insights endpoints.
- Feedback endpoint.
- WebSocket live match channel.
- Antonio AI commentary/prediction contract draft.
- Health and version endpoints.
- OpenAPI docs from FastAPI.

## Run Locally

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

- API health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Demo Login

```json
{
  "email": "demo@fanatlas.app",
  "password": "password123"
}
```

## Endpoint Map

| Area | Endpoint |
| --- | --- |
| Health | `GET /health` |
| Version | `GET /version` |
| Auth | `POST /api/v1/auth/signup` |
| Auth | `POST /api/v1/auth/login` |
| Auth | `POST /api/v1/auth/refresh` |
| Auth | `POST /api/v1/auth/logout` |
| User | `GET /api/v1/me` |
| User | `PATCH /api/v1/me/profile` |
| Matches | `GET /api/v1/matches` |
| Matches | `GET /api/v1/matches/{match_id}` |
| Match Center | `GET /api/v1/matches/{match_id}/center` |
| Timeline | `GET /api/v1/matches/{match_id}/timeline` |
| Commentary | `GET /api/v1/matches/{match_id}/commentary` |
| Predictions | `GET /api/v1/matches/{match_id}/predictions` |
| Predictions | `POST /api/v1/predictions` |
| Community | `GET /api/v1/matches/{match_id}/community-prediction` |
| Leaderboard | `GET /api/v1/leaderboard` |
| Insights | `GET /api/v1/matches/{match_id}/insights` |
| Feedback | `POST /api/v1/feedback` |
| Realtime | `WS /api/v1/ws/matches/{match_id}` |

## WebSocket Contract

Connect to:

```text
ws://127.0.0.1:8000/api/v1/ws/matches/{match_id}
```

Initial server message:

```json
{
  "type": "match.snapshot",
  "match_id": "match-aur-har",
  "sequence": 0,
  "payload": {
    "match": {},
    "timeline": [],
    "commentary": [],
    "stream_status": "available"
  }
}
```

Client ping:

```json
{ "type": "ping" }
```

Server response:

```json
{ "type": "pong", "match_id": "match-aur-har", "sequence": 1, "payload": { "status": "ok" } }
```

See `docs/antonio-ai-contract.md` for the AI layer compatibility contract.

## Next Build Steps

1. Connect Figma screens to endpoint response needs.
2. Finalize OpenAPI schemas with frontend.
3. Replace selected seed data with a free football API adapter.
4. Add persistent database storage.
5. Add WebSocket live match channel.
6. Wire Antonio's AI commentary and prediction API contracts when ready.
