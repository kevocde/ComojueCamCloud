# ComojueCam Cloud

Servidor de telemetría para la aplicación Android ComojueCam.

## Características

- Recepción de telemetría vía WebSocket
- Almacenamiento persistente en SQLite
- Interfaz web para visualizar datos de clientes
- Validación de tokens con formato `xxx-xxx`

## Instalación

```bash
uv sync
```

## Uso

### Iniciar el servidor

```bash
uv run comojuecamcloud
```

El servidor estará disponible en `http://localhost:8000`

### Endpoints

- **WebSocket**: `ws://localhost:8000/ws/{token}` - Conexión de clientes
- **Web UI**: `http://localhost:8000/clients` - Lista de clientes activos

### Formato del token

El token debe tener el formato `xxx-xxx` donde `x` es un carácter alfanumérico. Ejemplo: `abc-xyz`, `A1b-X2y`

### Formato de datos de telemetría

El cliente debe enviar un JSON con la siguiente estructura:

```json
{
  "1697456789": {
    "gyroscope": {"x": 1.5, "y": 2.3, "z": 3.7},
    "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8},
    "velocity": {"speed": 45.5},
    "gps": {"latitude": 19.4326, "longitude": -99.1332}
  }
}
```

Donde la key es un timestamp Unix y el valor contiene las categorías de telemetría.

## Testing

```bash
uv run pytest tests/ -v
```

## Cliente de prueba

Ejecuta el cliente de prueba para simular una conexión:

```bash
uv run python examples/test_client.py
```

## Estructura del proyecto

```
src/comojuecamcloud/
├── __init__.py          # Entry point
├── app.py               # Configuración FastAPI
├── database.py          # SQLAlchemy + SQLite
├── models/              # Modelos de base de datos
├── schemas/             # Pydantic schemas
├── api/                 # Endpoints (WebSocket + REST)
├── services/            # Lógica de negocio
└── templates/           # HTML templates
```

## Configuración

Variables de entorno opcionales:

- `DATABASE_URL`: URL de la base de datos (default: SQLite local)
