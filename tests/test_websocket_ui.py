import pytest
from fastapi.testclient import TestClient

from comojuecamcloud.app import app


def test_ws_ui_clients_accepts_connection():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/ui/clients") as ws:
            ws.send_text("ping")


def test_ws_ui_detail_accepts_connection():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/ui/abc-xyz") as ws:
            ws.send_text("ping")
