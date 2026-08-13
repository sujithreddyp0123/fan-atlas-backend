from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login() -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@fanatlas.app", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health() -> None:
    response = client.get("/health", headers={"X-Request-ID": "req-test-health"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "req-test-health"


def test_login_and_me() -> None:
    token = login()
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "demo@fanatlas.app"


def test_match_center() -> None:
    response = client.get("/api/v1/matches/match-aur-har/center")
    assert response.status_code == 200
    body = response.json()
    assert body["match"]["id"] == "match-aur-har"
    assert body["ai_prediction"]["market"] == "match_result"
    assert "commentary" in body


def test_prediction_submission_requires_auth() -> None:
    response = client.post(
        "/api/v1/predictions",
        json={"match_id": "match-met-riv", "choice": "home"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
    assert "X-Request-ID" in response.headers


def test_prediction_submission_for_upcoming_match() -> None:
    token = login()
    response = client.post(
        "/api/v1/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json={"match_id": "match-met-riv", "choice": "home"},
    )
    assert response.status_code == 201
    assert response.json()["match_id"] == "match-met-riv"


def test_match_websocket_snapshot_and_ping() -> None:
    with client.websocket_connect("/api/v1/ws/matches/match-aur-har") as websocket:
        snapshot = websocket.receive_json()
        assert snapshot["type"] == "match.snapshot"
        assert snapshot["match_id"] == "match-aur-har"
        assert snapshot["payload"]["match"]["id"] == "match-aur-har"

        clock = websocket.receive_json()
        assert clock["type"] == "match.clock"

        commentary = websocket.receive_json()
        assert commentary["type"] == "commentary.available"

        websocket.send_json({"type": "ping"})
        pong = websocket.receive_json()
        assert pong["type"] == "pong"
        assert pong["payload"]["status"] == "ok"


def test_missing_match_uses_standard_error_shape() -> None:
    response = client.get("/api/v1/matches/missing-match")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "Match not found"
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]


def test_openapi_export_shape() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert body["info"]["title"] == "FanAtlas Universal Backend"
    assert "/api/v1/matches/{match_id}/center" in body["paths"]
