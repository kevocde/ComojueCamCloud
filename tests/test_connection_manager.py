import pytest
from unittest.mock import AsyncMock, MagicMock

from comojuecamcloud.websocket_manager import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect_clients(manager):
    ws = AsyncMock()
    await manager.connect_clients(ws)
    assert ws in manager._clients_sockets


@pytest.mark.asyncio
async def test_connect_detail(manager):
    ws = AsyncMock()
    await manager.connect_detail(ws, "abc-xyz")
    assert ws in manager._detail_sockets["abc-xyz"]


@pytest.mark.asyncio
async def test_disconnect_removes_from_all(manager):
    ws = AsyncMock()
    await manager.connect_clients(ws)
    await manager.connect_detail(ws, "abc-xyz")
    await manager.disconnect(ws)
    assert ws not in manager._clients_sockets
    assert ws not in manager._detail_sockets["abc-xyz"]


@pytest.mark.asyncio
async def test_broadcast_clients_sends_to_all_subscribers(manager):
    ws1, ws2 = AsyncMock(), AsyncMock()
    await manager.connect_clients(ws1)
    await manager.connect_clients(ws2)

    await manager.broadcast_clients({"type": "update"})

    ws1.send_json.assert_awaited_once_with({"type": "update"})
    ws2.send_json.assert_awaited_once_with({"type": "update"})


@pytest.mark.asyncio
async def test_broadcast_detail_sends_only_to_token_subscribers(manager):
    ws_abc, ws_def = AsyncMock(), AsyncMock()
    await manager.connect_detail(ws_abc, "abc-xyz")
    await manager.connect_detail(ws_def, "def-uvw")

    await manager.broadcast_detail("abc-xyz", {"type": "telemetry"})

    ws_abc.send_json.assert_awaited_once_with({"type": "telemetry"})
    ws_def.send_json.assert_not_awaited()


@pytest.mark.asyncio
async def test_broadcast_handles_disconnected_socket(manager):
    ws_ok = AsyncMock()
    ws_fail = AsyncMock()
    ws_fail.send_json.side_effect = Exception("disconnected")
    await manager.connect_clients(ws_ok)
    await manager.connect_clients(ws_fail)

    await manager.broadcast_clients({"type": "update"})

    ws_ok.send_json.assert_awaited_once_with({"type": "update"})
