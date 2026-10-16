import json
from typing import Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from comojuecamcloud.models.client import TelemetryBatch, TelemetryData


class TelemetryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_batch(
        self, client_token: str, timestamp: int, data: Dict[str, Any]
    ) -> TelemetryBatch:
        batch = TelemetryBatch(client_token=client_token, timestamp=timestamp)
        self.db.add(batch)
        await self.db.flush()

        for category, values in data.items():
            telemetry_data = TelemetryData(
                batch_id=batch.id,
                category=category,
                values_json=json.dumps(values)
            )
            self.db.add(telemetry_data)

        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def get_batches(self, client_token: str) -> List[TelemetryBatch]:
        result = await self.db.execute(
            select(TelemetryBatch)
            .where(TelemetryBatch.client_token == client_token)
            .order_by(TelemetryBatch.timestamp.desc())
        )
        return result.scalars().all()

    async def get_batch(self, client_token: str, timestamp: int) -> TelemetryBatch:
        result = await self.db.execute(
            select(TelemetryBatch)
            .where(
                TelemetryBatch.client_token == client_token,
                TelemetryBatch.timestamp == timestamp
            )
        )
        return result.scalar_one_or_none()

    async def get_telemetry_data(self, batch_id: int) -> List[TelemetryData]:
        result = await self.db.execute(
            select(TelemetryData).where(TelemetryData.batch_id == batch_id)
        )
        return result.scalars().all()
