from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

    token = Column(String(7), primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_seen = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    telemetry_batches = relationship(
        "TelemetryBatch", back_populates="client", cascade="all, delete-orphan"
    )


class TelemetryBatch(Base):
    __tablename__ = "telemetry_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_token = Column(String(7), ForeignKey("clients.token"), nullable=False)
    timestamp = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    client = relationship("Client", back_populates="telemetry_batches")
    telemetry_data = relationship(
        "TelemetryData", back_populates="batch", cascade="all, delete-orphan"
    )


class TelemetryData(Base):
    __tablename__ = "telemetry_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("telemetry_batches.id"), nullable=False)
    category = Column(String(50), nullable=False)
    values_json = Column(Text, nullable=False)

    batch = relationship("TelemetryBatch", back_populates="telemetry_data")
