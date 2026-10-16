import pytest

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
    assert client.is_active is True


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
async def test_set_inactive(db):
    service = ClientService(db)
    client = await service.get_or_create("abc-xyz")
    assert client.is_active is True

    await service.set_inactive("abc-xyz")
    client = await service.get_client("abc-xyz")
    assert client.is_active is False


@pytest.mark.asyncio
async def test_get_active_clients(db):
    service = ClientService(db)
    await service.get_or_create("abc-xyz")
    await service.get_or_create("def-uvw")
    await service.get_or_create("ghi-rst")

    clients = await service.get_active_clients()
    assert len(clients) == 3

    await service.set_inactive("abc-xyz")
    clients = await service.get_active_clients()
    assert len(clients) == 2
