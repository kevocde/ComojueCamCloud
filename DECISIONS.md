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

### Giroscopio (2D)
- Brújula 2D SVG simple (sin Three.js)
  - Aguja que rota según heading (yaw del magnetómetro)
  - Puntos cardinales N/E/S/W
  - Display de heading con dirección cardinal
- **Sensor fusion (complementary filter)** combinando:
  - Giroscopio (velocidad angular integrada)
  - Acelerómetro (roll/pitch derivado de gravedad)
  - Magnetómetro (heading compensado por tilt)
- Fórmula: `orientation = 0.96 * gyro_integrated + 0.04 * accel/mag`
- **Ajuste de roll**: `pitch_adjusted = 90 - roll_deg` para representar inclinación correcta
  - 0° = nivel, negativo = apunta hacia abajo, positivo = apunta hacia arriba
- **Indicador de horizonte artificial**:
  - SVG circular con cielo (azul) y suelo (marrón)
  - Línea del horizonte SIEMPRE horizontal
  - Cielo/suelo se desplazan verticalmente según pitch_adjusted (no rota)
  - Marcas de referencia fijas indicando el punto de vista
  - Display de inclinación en grados debajo del indicador
- Display de Roll, Pitch, Yaw, Heading en grid responsive

### GPS
- Coordenadas lat/lon del último batch
- Link directo a Google Maps: `https://www.google.com/maps?q=lat,lon`

### Datos de telemetría recibidos
- `gyroscope`: {x, y, z} — velocidad angular (deg/s)
- `accelerometer`: {x, y, z} — aceleración (m/s²)
- `magnetometer`: {x, y, z} — campo magnético (µT)
- `gps`: {latitude, longitude}

### Gestión de clientes (feature/client-management)
- **Actividad por tiempo**: cliente activo si recibió datos en últimos 5 minutos
- Campo calculado `is_recently_active` basado en `last_seen` (no en conexión WebSocket)
- Endpoint `DELETE /clients/{token}` para eliminar clientes
- Botón eliminar en UI con confirmación
- WebSocket notifica `client_deleted` para actualización en tiempo real
- Umbral configurable: `ACTIVE_THRESHOLD_MINUTES = 5`

### Correcciones de flujo
- Commits de UI hechos inicialmente en main directamente (incorrecto)
- Movidos a rama `feature/ui-improvements` para seguir workflow correcto
- Main reseteado a `e73a547` (merge PR #3)
- PR pendiente para merge a main

---

## Notas técnicas

### Servicios agregados
- `ClientService.get_all_clients()` — retorna todos ordenados (activos primero)
- `TelemetryService.get_batches_with_data()` — batches con datos parseados

### Tests
- 34 tests pasando
- Tests para ConnectionManager, endpoints WS UI, servicios, gestión de clientes

### Workflow
- Commits progresivos con TDD (tests primero)
- Ramas: `feature/retro-ui`, `feature/live-ui`, `feature/ui-improvements`, `feature/client-management`
- Push inmediato tras cada cambio
- NUNCA merge directo a main, siempre usar PR
