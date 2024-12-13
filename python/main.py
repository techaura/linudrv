import asyncio
import websockets
import ssl
import os
import subprocess

# Параметры конфигурации
HOST = "0.0.0.0"
PORT = 8765

# Путь к директории и файлам
cert_dir = "misc"
cert_file = os.path.join(cert_dir, "certificate.pem")
key_file = os.path.join(cert_dir, "private-key.pem")

# Создание директории, если она не существует
if not os.path.exists(cert_dir):
    os.makedirs(cert_dir)
    print(f"Директория {cert_dir} создана")

# Проверяем, что файлы сертификатов и ключей существуют
# Проверка наличия сертификатов и ключей, если их нет - генерируем
if not os.path.exists(cert_file) or not os.path.exists(key_file):
    print("Сертификаты или ключи не найдены. Генерация...")
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", key_file, "-out", cert_file, "-days", "365", "-nodes"])
    print(f"Сертификат и ключ созданы в {cert_dir}")

# Настройка SSL
try:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    print("SSL контекст успешно настроен.")
except ssl.SSLError as e:
    print(f"Ошибка SSL: {e}")

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