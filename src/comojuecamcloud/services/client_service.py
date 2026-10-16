import re
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from comojuecamcloud.models.client import Client


class ClientService:
    TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9]{3}-[a-zA-Z0-9]{3}$")

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
            client.last_seen = datetime.now(UTC)
            client.is_active = True
            await self.db.commit()
            await self.db.refresh(client)

        return client

    async def set_inactive(self, token: str):
        result = await self.db.execute(select(Client).where(Client.token == token))
        client = result.scalar_one_or_none()
        if client:
            client.is_active = False
            await self.db.commit()

    async def get_active_clients(self):
        result = await self.db.execute(select(Client).where(Client.is_active == True))
        return result.scalars().all()

    async def get_client(self, token: str) -> Optional[Client]:
        result = await self.db.execute(select(Client).where(Client.token == token))
        return result.scalar_one_or_none()
