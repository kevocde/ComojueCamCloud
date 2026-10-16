import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService


@pytest.mark.asyncio
async def test_clients_page_retro_base_style(client: AsyncClient):
    response = await client.get("/clients")
    assert response.status_code == 200
    html = response.text
    assert "class=\"crt\"" in html
    assert "monospace" in html or "monospac" in html
    assert "#33ff33" in html or "33ff33" in html


@pytest.mark.asyncio
async def test_clients_page_ascii_decorations(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        cs = ClientService(db)
        await cs.get_or_create("abc-xyz")

    response = await client.get("/clients")
    html = response.text
    assert "╔" in html or "┌" in html or "+" in html


@pytest.mark.asyncio
async def test_clients_page_retro_status_indicators(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        cs = ClientService(db)
        await cs.get_or_create("abc-xyz")

    response = await client.get("/clients")
    html = response.text
    assert "[*]" in html or "[ONLINE]" in html or "[OK]" in html


@pytest.mark.asyncio
async def test_clients_page_breadcrumb_in_detail(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        cs = ClientService(db)
        await cs.get_or_create("abc-xyz")

    response = await client.get("/clients/abc-xyz")
    html = response.text
    assert "cd" in html.lower() or ".." in html or "&lt;-" in html or "←" in html


@pytest.mark.asyncio
async def test_error_page_retro_style(client: AsyncClient):
    response = await client.get("/clients/nonexistent")
    assert response.status_code == 404
    html = response.text
    assert "class=\"crt\"" in html
    assert "404" in html
    assert "ERROR" in html or "error" in html


@pytest.mark.asyncio
async def test_telemetry_detail_retro_table(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        cs = ClientService(db)
        ts = TelemetryService(db)
        await cs.get_or_create("abc-xyz")
        await ts.save_batch("abc-xyz", 1697456789, {"gyroscope": {"x": 1.5}})

    response = await client.get("/clients/abc-xyz/1697456789")
    html = response.text
    assert "class=\"crt\"" in html
    assert "─" in html or "│" in html or "|" in html
