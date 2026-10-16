from typing import Any, Dict

from pydantic import BaseModel, Field


class TelemetryDataSchema(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp")
    gyroscope: Dict[str, float] = Field(default_factory=dict)
    accelerometer: Dict[str, float] = Field(default_factory=dict)
    velocity: Dict[str, float] = Field(default_factory=dict)
    gps: Dict[str, float] = Field(default_factory=dict)

    class Config:
        extra = "allow"
