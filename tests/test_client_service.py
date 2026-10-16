import pytest
from datetime import datetime, timedelta

from comojuecamcloud.services.client_service import ClientService


@pytest.mark.asyncio
async def test_validate_token_valid(db):
    service = ClientService(db)
    assert service.validate_token("abc-xyz") is True
    assert service.validate_token("ABC-XYZ") is True
    assert service.validate_token("a1b-x2y") is True


@pytest.mark.asyncio
async def test_validate_token_invalid(db):
    service = ClientService(db)
    assert service.validate_token("invalid") is False
    assert service.validate_token("abc-") is False
    assert service.validate_token("-xyz") is False
    assert service.validate_token("abcxyz") is False
    assert service.validate_token("abc-xyz-123") is False
    assert service.validate_token("abc1-xyz") is False


@pytest.mark.asyncio
async def test_get_or_create_new_client(db):
    service = ClientService(db)
    client = await service.get_or_create("abc-xyz")

    assert client is not None
    assert client.token == "abc-xyz"


@pytest.mark.asyncio
async def test_get_or_create_existing_client(db):
    service = ClientService(db)
    client1 = await service.get_or_create("abc-xyz")
    client2 = await service.get_or_create("abc-xyz")

    assert client1.token == client2.token


@pytest.mark.asyncio
async def test_get_or_create_invalid_token(db):
    service = ClientService(db)
    client = await service.get_or_create("invalid")

    assert client is None


@pytest.mark.asyncio
async def test_get_all_clients_with_time_based_active(db):
    service = ClientService(db)
    await service.get_or_create("abc-xyz")
    await service.get_or_create("def-uvw")
    await service.get_or_create("ghi-rst")

    client = await service.get_client("def-uvw")
    client.last_seen = datetime.utcnow() - timedelta(minutes=2)
    await db.commit()

    clients = await service.get_all_clients()
    assert len(clients) == 3

    active_clients = [c for c in clients if c.is_recently_active]
    assert len(active_clients) == 2


@pytest.mark.asyncio
async def test_delete_client(db):
    service = ClientService(db)
    await service.get_or_create("abc-xyz")

    client = await service.get_client("abc-xyz")
    assert client is not None

    result = await service.delete_client("abc-xyz")
    assert result is True

    client = await service.get_client("abc-xyz")
    assert client is None


@pytest.mark.asyncio
async def test_delete_nonexistent_client(db):
    service = ClientService(db)
    result = await service.delete_client("nonexistent")
    assert result is False
