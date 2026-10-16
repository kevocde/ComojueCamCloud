import pytest

from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService


@pytest.mark.asyncio
async def test_save_batch(db):
    client_service = ClientService(db)
    telemetry_service = TelemetryService(db)

    client = await client_service.get_or_create("abc-xyz")
    assert client is not None

    timestamp = 1697456789
    data = {
        "gyroscope": {"x": 1.5, "y": 2.3, "z": 3.7},
        "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8},
        "velocity": {"speed": 45.5},
        "gps": {"latitude": 19.4326, "longitude": -99.1332}
    }

    batch = await telemetry_service.save_batch(client.token, timestamp, data)

    assert batch is not None
    assert batch.client_token == "abc-xyz"
    assert batch.timestamp == timestamp


@pytest.mark.asyncio
async def test_get_batches(db):
    client_service = ClientService(db)
    telemetry_service = TelemetryService(db)

    client = await client_service.get_or_create("abc-xyz")

    await telemetry_service.save_batch("abc-xyz", 1697456789, {"test": {}})
    await telemetry_service.save_batch("abc-xyz", 1697456799, {"test": {}})
    await telemetry_service.save_batch("abc-xyz", 1697456809, {"test": {}})

    batches = await telemetry_service.get_batches("abc-xyz")

    assert len(batches) == 3
    assert batches[0].timestamp == 1697456809
    assert batches[1].timestamp == 1697456799
    assert batches[2].timestamp == 1697456789


@pytest.mark.asyncio
async def test_get_batch(db):
    client_service = ClientService(db)
    telemetry_service = TelemetryService(db)

    await client_service.get_or_create("abc-xyz")
    await telemetry_service.save_batch("abc-xyz", 1697456789, {"test": {}})

    batch = await telemetry_service.get_batch("abc-xyz", 1697456789)

    assert batch is not None
    assert batch.timestamp == 1697456789


@pytest.mark.asyncio
async def test_get_telemetry_data(db):
    client_service = ClientService(db)
    telemetry_service = TelemetryService(db)

    await client_service.get_or_create("abc-xyz")
    data = {
        "gyroscope": {"x": 1.5, "y": 2.3, "z": 3.7},
        "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8}
    }
    batch = await telemetry_service.save_batch("abc-xyz", 1697456789, data)

    telemetry_data = await telemetry_service.get_telemetry_data(batch.id)

    assert len(telemetry_data) == 2
    categories = {d.category for d in telemetry_data}
    assert "gyroscope" in categories
    assert "accelerometer" in categories


@pytest.mark.asyncio
async def test_get_batches_with_data(db):
    client_service = ClientService(db)
    telemetry_service = TelemetryService(db)

    await client_service.get_or_create("abc-xyz")
    data = {
        "gyroscope": {"x": 1.5, "y": 2.3, "z": 3.7},
        "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8}
    }
    await telemetry_service.save_batch("abc-xyz", 1697456789, data)

    batches = await telemetry_service.get_batches_with_data("abc-xyz")

    assert len(batches) == 1
    batch = batches[0]
    assert batch["timestamp"] == 1697456789
    assert "gyroscope" in batch["data"]
    assert batch["data"]["gyroscope"]["x"] == 1.5
