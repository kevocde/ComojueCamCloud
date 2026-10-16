import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService


@pytest.mark.asyncio
async def test_list_clients_empty(client: AsyncClient):
    response = await client.get("/clients")
    assert response.status_code == 200
    assert "No hay clientes activos" in response.text


@pytest.mark.asyncio
async def test_list_clients_with_data(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        client_service = ClientService(db)
        await client_service.get_or_create("abc-xyz")
        await client_service.get_or_create("def-uvw")

    response = await client.get("/clients")
    assert response.status_code == 200
    assert "abc-xyz" in response.text
    assert "def-uvw" in response.text


@pytest.mark.asyncio
async def test_client_detail(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        client_service = ClientService(db)
        await client_service.get_or_create("abc-xyz")

    response = await client.get("/clients/abc-xyz")
    assert response.status_code == 200
    assert "abc-xyz" in response.text


@pytest.mark.asyncio
async def test_client_detail_not_found(client: AsyncClient):
    response = await client.get("/clients/not-found")
    assert response.status_code == 404
    assert "Client not found" in response.text


@pytest.mark.asyncio
async def test_telemetry_detail(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        client_service = ClientService(db)
        telemetry_service = TelemetryService(db)

        await client_service.get_or_create("abc-xyz")
        await telemetry_service.save_batch(
            "abc-xyz",
            1697456789,
            {
                "gyroscope": {"x": 1.5, "y": 2.3, "z": 3.7},
                "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8}
            }
        )

    response = await client.get("/clients/abc-xyz/1697456789")
    assert response.status_code == 200
    assert "1697456789" in response.text
    assert "gyroscope" in response.text
    assert "accelerometer" in response.text


@pytest.mark.asyncio
async def test_telemetry_detail_not_found(client: AsyncClient, test_db: async_sessionmaker):
    async with test_db() as db:
        client_service = ClientService(db)
        await client_service.get_or_create("abc-xyz")

    response = await client.get("/clients/abc-xyz/9999999999")
    assert response.status_code == 404
    assert "Telemetry data not found" in response.text
