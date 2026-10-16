import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from comojuecamcloud.database import async_session_factory
from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService

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

                await client_service.get_or_create(client.token)
                await websocket.send_json({"status": "ok"})

        except WebSocketDisconnect:
            await client_service.set_inactive(client.token)
