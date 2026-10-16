from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ClientSchema(BaseModel):
    token: str
    created_at: datetime
    last_seen: datetime
    is_active: bool

    class Config:
        from_attributes = True
