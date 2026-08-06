from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.repositories.store import get_store
from app.schemas.realtime import RealtimeEnvelope

router = APIRouter()


@router.websocket("/ws/matches/{match_id}")
async def match_socket(websocket: WebSocket, match_id: str) -> None:
    store = get_store()
    snapshot = store.get_live_snapshot(match_id)
    if snapshot is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    sequence = 0
    await websocket.send_json(
        RealtimeEnvelope(
            type="match.snapshot",
            match_id=match_id,
            sequence=sequence,
            payload=snapshot,
        ).model_dump(mode="json")
    )

    for event in store.get_seeded_live_events(match_id):
        sequence += 1
        await websocket.send_json(
            RealtimeEnvelope(
                type=event["type"],
                match_id=match_id,
                sequence=sequence,
                payload=event["payload"],
            ).model_dump(mode="json")
        )

    try:
        while True:
            message = await websocket.receive_json()
            sequence += 1
            if message.get("type") == "ping":
                await websocket.send_json(
                    RealtimeEnvelope(
                        type="pong",
                        match_id=match_id,
                        sequence=sequence,
                        payload={"status": "ok"},
                    ).model_dump(mode="json")
                )
            else:
                await websocket.send_json(
                    RealtimeEnvelope(
                        type="error",
                        match_id=match_id,
                        sequence=sequence,
                        payload={"message": "Unsupported realtime message type"},
                    ).model_dump(mode="json")
                )
    except WebSocketDisconnect:
        return

