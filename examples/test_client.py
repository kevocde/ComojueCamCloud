#!/usr/bin/env python3
import asyncio
import json
import time
import websockets


async def send_telemetry(token: str = "abc-xyz"):
    uri = f"ws://localhost:8000/ws/{token}"

    async with websockets.connect(uri) as websocket:
        print(f"Conectado con token: {token}")

        while True:
            timestamp = int(time.time())

            telemetry_data = {
                str(timestamp): {
                    "gyroscope": {
                        "x": 1.5,
                        "y": 2.3,
                        "z": 3.7
                    },
                    "accelerometer": {
                        "x": 0.1,
                        "y": 0.2,
                        "z": 9.8
                    },
                    "velocity": {
                        "speed": 45.5
                    },
                    "gps": {
                        "latitude": 19.4326,
                        "longitude": -99.1332
                    }
                }
            }

            await websocket.send(json.dumps(telemetry_data))
            response = await websocket.recv()
            print(f"Enviado: {timestamp} - Respuesta: {response}")

            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(send_telemetry())
