import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService


@pytest.mark.asyncio
async def test_clients_page_modern_dark_theme(client: AsyncClient):
    response = await client.get("/clients")
    html = response.text
    assert response.status_code == 200
    assert "#1a1b26" in html
    assert "monospace" in html
    assert "border-radius" in html
    assert "box-shadow" in html


@pytest.mark.asyncio
async def test_clients_page_uses_cards_not_borders(client: AsyncClient):
    response = await client.get("/clients")
    html = response.text
    assert "class=\"card\"" in html or "card-" in html
    assert "╔" not in html
    assert "┌" not in html


@pytest.mark.asyncio
async def test_clients_page_status_dot(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        cs = ClientService(db)
        await cs.get_or_create("abc-xyz")
    response = await client.get("/clients")
    html = response.text
    assert "dot" in html or "status" in html


@pytest.mark.asyncio
async def test_error_page_modern_style(client: AsyncClient):
    response = await client.get("/clients/nonexistent")
    assert response.status_code == 404
    html = response.text
    assert "#1a1b26" in html
    assert "border-radius" in html


@pytest.mark.asyncio
async def test_telemetry_detail_clean_table(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        cs = ClientService(db)
        ts = TelemetryService(db)
        await cs.get_or_create("abc-xyz")
        await ts.save_batch("abc-xyz", 1697456789, {"gyroscope": {"x": 1.5}})

    response = await client.get("/clients/abc-xyz/1697456789")
    html = response.text
    assert "#1a1b26" in html
    assert "box-shadow" in html
    assert "border-radius" in html
