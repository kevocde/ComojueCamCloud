import uvicorn

from comojuecamcloud.app import app


def main() -> None:
    uvicorn.run(
        "comojuecamcloud.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
