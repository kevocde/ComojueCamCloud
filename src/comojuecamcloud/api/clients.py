import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from comojuecamcloud.database import get_db
from comojuecamcloud.services.client_service import ClientService
from comojuecamcloud.services.telemetry_service import TelemetryService

router = APIRouter()
templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(templates_dir)), auto_reload=True)


@router.get("/clients")
async def list_clients(request: Request, db: AsyncSession = Depends(get_db)):
    client_service = ClientService(db)
    clients = await client_service.get_active_clients()

    template = env.get_template("clients.html")
    html = template.render(request=request, clients=clients)
    return HTMLResponse(content=html)


@router.get("/clients/{token}")
async def client_detail(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    client_service = ClientService(db)
    telemetry_service = TelemetryService(db)

    client = await client_service.get_client(token)
    if not client:
        template = env.get_template("error.html")
        html = template.render(request=request, error="Client not found")
        return HTMLResponse(content=html, status_code=404)

    batches = await telemetry_service.get_batches(token)

    template = env.get_template("client_detail.html")
    html = template.render(request=request, client=client, batches=batches)
    return HTMLResponse(content=html)


@router.get("/clients/{token}/{timestamp}")
async def telemetry_detail(
    request: Request, token: str, timestamp: int, db: AsyncSession = Depends(get_db)
):
    telemetry_service = TelemetryService(db)

    batch = await telemetry_service.get_batch(token, timestamp)
    if not batch:
        template = env.get_template("error.html")
        html = template.render(request=request, error="Telemetry data not found")
        return HTMLResponse(content=html, status_code=404)

    telemetry_data = await telemetry_service.get_telemetry_data(batch.id)

    data_by_category = {}
    for data in telemetry_data:
        data_by_category[data.category] = json.loads(data.values_json)

    template = env.get_template("telemetry_detail.html")
    html = template.render(
        request=request,
        token=token,
        timestamp=timestamp,
        datetime=datetime.fromtimestamp(timestamp),
        data_by_category=data_by_category
    )
    return HTMLResponse(content=html)
