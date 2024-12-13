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

# Проверяем наличие директории и создаем ее, если она не существует
if not os.path.exists(cert_dir):
    os.makedirs(cert_dir)
    print(f"Директория {cert_dir} создана")

# Проверяем наличие сертификатов и ключей
if not os.path.exists(cert_file) or not os.path.exists(key_file):
    print("Сертификаты или ключи не найдены. Генерация...")

    # Генерация сертификатов и ключей с помощью OpenSSL
    result = subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", key_file, "-out", cert_file, "-days", "365", "-nodes"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Проверка, что команда выполнена успешно
    if result.returncode == 0:
        print(f"Сертификат и ключ успешно созданы в {cert_dir}")
    else:
        print(f"Ошибка при создании сертификатов и ключей: {result.stderr.decode()}")
        exit(1)

# Настройка SSL
try:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    print("SSL контекст успешно настроен.")
except ssl.SSLError as e:
    print(f"Ошибка SSL: {e}")
except FileNotFoundError as e:
    print(f"Ошибка: {e}")


# Обработчик WebSocket-сообщений
async def handler(websocket, path):
    try:
        print(f"New connection from {websocket.remote_address}")

        # Принимаем сообщение от клиента
        message = await websocket.recv()
        print(f"Received message: {message}")

        # Отправляем сообщение обратно клиенту
        response = f"Echo: {message}"
        await websocket.send(response)
        print(f"Sent response: {response}")
    except Exception as e:
        print(f"Error during communication: {e}")
    finally:
        await websocket.close()


# Основная функция запуска сервера
async def main():
    server = await websockets.serve(
        handler,
        HOST,
        PORT,
        ssl=ssl_context
    )
    print(f"Server started at wss://{HOST}:{PORT}")

    # Запускаем сервер и ждем завершения
    await server.wait_closed()


# Запуск сервера
if __name__ == "__main__":
    asyncio.run(main())