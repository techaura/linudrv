import asyncio
import websockets
import ssl

# Параметры конфигурации
HOST = "0.0.0.0"
PORT = 8765
CERT_FILE = "/path/to/certificate.pem"  # Путь к SSL-сертификату
KEY_FILE = "/path/to/private-key.pem"  # Путь к закрытому ключу

# Обработчик сообщений
async def handler(websocket, path):
    print("Client connected:", websocket.remote_address)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected: {e}")

# Настройка SSL
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

# Запуск сервера
async def main():
    server = await websockets.serve(
        handler,
        HOST,
        PORT,
        ssl=ssl_context
    )
    print(f"WebSocket server started on wss://{HOST}:{PORT}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())