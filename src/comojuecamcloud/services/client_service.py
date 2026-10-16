import re
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from comojuecamcloud.models.client import Client


class ClientService:
    TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9]{3}-[a-zA-Z0-9]{3}$")
    ACTIVE_THRESHOLD_MINUTES = 5

    def __init__(self, db: AsyncSession):
        self.db = db

    def validate_token(self, token: str) -> bool:
        return bool(self.TOKEN_PATTERN.match(token))

    async def get_or_create(self, token: str) -> Optional[Client]:
        if not self.validate_token(token):
            return None

        result = await self.db.execute(select(Client).where(Client.token == token))
        client = result.scalar_one_or_none()

        if client is None:
            client = Client(token=token)
            self.db.add(client)
            await self.db.commit()
            await self.db.refresh(client)
        else:
            client.last_seen = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(client)

        return client

    async def get_all_clients(self):
        result = await self.db.execute(
            select(Client).order_by(Client.last_seen.desc())
        )
        clients = result.scalars().all()
        threshold = datetime.utcnow() - timedelta(minutes=self.ACTIVE_THRESHOLD_MINUTES)

        for client in clients:
            client.is_recently_active = client.last_seen >= threshold

        return clients

    async def get_client(self, token: str) -> Optional[Client]:
        result = await self.db.execute(select(Client).where(Client.token == token))
        client = result.scalar_one_or_none()
        if client:
            threshold = datetime.utcnow() - timedelta(minutes=self.ACTIVE_THRESHOLD_MINUTES)
            client.is_recently_active = client.last_seen >= threshold
        return client

    async def delete_client(self, token: str) -> bool:
        result = await self.db.execute(select(Client).where(Client.token == token))
        client = result.scalar_one_or_none()
        if not client:
            return False

        await self.db.delete(client)
        await self.db.commit()
        return True
