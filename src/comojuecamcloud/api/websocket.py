import json
from datetime import datetime, UTC
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from comojuecamcloud.database import async_session_factory
from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService
from comojuecamcloud.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    async with async_session_factory() as db:
        client_service = ClientService(db)
        telemetry_service = TelemetryService(db)

        client = await client_service.get_or_create(token)
        if not client:
            await websocket.close(code=1008)
            return

        await websocket.accept()

        await manager.broadcast_clients({
            "type": "client_update",
            "token": token,
            "last_seen": client.last_seen.isoformat()
        })

        try:
            while True:
                data = await websocket.receive_text()

                try:
                    telemetry_dict = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_json({"error": "Invalid JSON"})
                    continue

                for timestamp_str, telemetry_data in telemetry_dict.items():
                    try:
                        timestamp = int(timestamp_str)
                        await telemetry_service.save_batch(
                            client.token, timestamp, telemetry_data
                        )
                    except (ValueError, TypeError):
                        await websocket.send_json({
                            "error": f"Invalid timestamp: {timestamp_str}"
                        })
                        continue

                    await manager.broadcast_detail(token, {
                        "type": "telemetry",
                        "token": token,
                        "timestamp": timestamp,
                        "data": telemetry_data
                    })

                    client = await client_service.get_or_create(client.token)
                    await manager.broadcast_clients({
                        "type": "client_update",
                        "token": token,
                        "last_seen": client.last_seen.isoformat()
                    })

                await websocket.send_json({"status": "ok"})

        except WebSocketDisconnect:
            pass


@router.websocket("/ws/ui/clients")
async def ws_ui_clients(websocket: WebSocket):
    await websocket.accept()
    await manager.connect_clients(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@router.websocket("/ws/ui/{token}")
async def ws_ui_detail(websocket: WebSocket, token: str):
    await websocket.accept()
    await manager.connect_detail(websocket, token)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
