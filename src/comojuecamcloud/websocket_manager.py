from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._clients_sockets: Set[WebSocket] = set()
        self._detail_sockets: Dict[str, Set[WebSocket]] = {}

    async def connect_clients(self, websocket: WebSocket):
        self._clients_sockets.add(websocket)

    async def connect_detail(self, websocket: WebSocket, token: str):
        if token not in self._detail_sockets:
            self._detail_sockets[token] = set()
        self._detail_sockets[token].add(websocket)

    async def disconnect(self, websocket: WebSocket):
        self._clients_sockets.discard(websocket)
        for sockets in self._detail_sockets.values():
            sockets.discard(websocket)

    async def broadcast_clients(self, message: dict):
        for ws in list(self._clients_sockets):
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)

    async def broadcast_detail(self, token: str, message: dict):
        if token in self._detail_sockets:
            for ws in list(self._detail_sockets[token]):
                try:
                    await ws.send_json(message)
                except Exception:
                    await self.disconnect(ws)


manager = ConnectionManager()
