# Decisiones de Desarrollo - ComojueCamCloud

## UI Retro / Modern Dark Theme (PR #2 - feature/retro-ui)

**Fecha**: Oct 16, 2026

### Decisiones de diseño
- Paleta inspirada en Catppuccin Mocha: `#1a1b26` background, `#89b4fa` accent
- Tipografía monoespaciada (`ui-monospace, SF Mono, Cascadia Code, Consolas`)
- Cards con `border-radius: 8px`, `box-shadow` sutil, sin bordes
- Hover con `translateY(-2px)` y sombra profunda
- CSS compartido en `templates/base.html` con variables CSS

### Rechazado
- Estilo terminal CRT verde fósforo (#33ff33 on #001100) — muy retro, no moderno
- Bordes ASCII / box-drawing characters
- Textos en ALL CAPS con letter-spacing

---

## Live UI con WebSockets (PR #3 - feature/live-ui)

**Fecha**: Oct 16, 2026

### Arquitectura WebSocket
- `ConnectionManager` en memoria (sin dependencias externas) en `websocket_manager.py`
- Endpoints UI: `/ws/ui/clients` (listado) y `/ws/ui/{token}` (detalle)
- Broadcast desde `/ws/{token}` tras guardar batch de telemetría
- Actualización parcial del DOM vía JS (sin recargar página)

### Listado de clientes
- Muestra TODOS los clientes (activos + inactivos)
- Activos primero, inactivos al final con estilo atenuado (opacity 0.5)
- WebSocket notifica cambios de estado en tiempo real

### Acelerómetro
- Procesamiento de señal:
  - Filtro paso-bajo para gravedad: `g[i] = 0.8 * g[i] + 0.2 * raw[i]`
  - Aceleración lineal: `lin[i] = raw[i] - g[i]`
  - Magnitud: `a = sqrt(lin.x² + lin.y² + lin.z²)` en m/s²
  - G-force: `G = a / 9.80665`
- Gráfico SVG time scale (tiempo vs Gs)
- Filtros de ventana: 5m, 10m, 30m, 1h
- Interpolación a 20 puntos para mejor resolución visual
- Escala dinámica del eje Y según datos en ventana

### Giroscopio (Three.js)
- Visualización 3D con Three.js (bus con carrocería, ventanas, 4 ruedas)
- **Sensor fusion (complementary filter)** combinando:
  - Giroscopio (velocidad angular integrada)
  - Acelerómetro (roll/pitch derivado de gravedad)
  - Magnetómetro (heading compensado por tilt)
- Fórmula: `orientation = 0.96 * gyro_integrated + 0.04 * accel/mag`
- Display: Roll, Pitch, Yaw en grados

### GPS
- Coordenadas lat/lon del último batch
- Link directo a Google Maps: `https://www.google.com/maps?q=lat,lon`

### Datos de telemetría recibidos
- `gyroscope`: {x, y, z} — velocidad angular (deg/s)
- `accelerometer`: {x, y, z} — aceleración (m/s²)
- `magnetometer`: {x, y, z} — campo magnético (µT)
- `gps`: {latitude, longitude}

---

## Notas técnicas

### Servicios agregados
- `ClientService.get_all_clients()` — retorna todos ordenados (activos primero)
- `TelemetryService.get_batches_with_data()` — batches con datos parseados

### Tests
- 32 tests pasando
- Tests para ConnectionManager, endpoints WS UI, servicios

### Workflow
- Commits progresivos con TDD (tests primero)
- Ramas: `feature/retro-ui`, `feature/live-ui`
- Push inmediato tras cada cambio
