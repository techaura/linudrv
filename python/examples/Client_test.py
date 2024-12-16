import asyncio
import ssl
import websockets

# Настройки клиента
HOST = "192.168.88.245"
PORT = 8765
URI = f"wss://{HOST}:{PORT}"  # URL для подключения к серверу

# SSL-контекст для защиты соединения
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False  # Отключаем проверку имени хоста
ssl_context.verify_mode = ssl.CERT_NONE  # Отключаем проверку сертификата (только для тестов!)

# Клиентская функция
async def test_client():
    try:
        async with websockets.connect(URI, ssl=ssl_context) as websocket:
            # Отправляем сообщение серверу
            message = "Hello, WebSocket Server!"
            print(f"Sending: {message}")
            await websocket.send(message)

            # Получаем ответ от сервера
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Error: {e}")

# Запуск клиента
if __name__ == "__main__":
    asyncio.run(test_client())
