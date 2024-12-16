import asyncio
import websockets
import ssl
import os
import subprocess

# Настройки
HOST = "localhost"
PORT = 8765
CERT_DIR = "misc"
CERT_FILE = os.path.join(CERT_DIR, "certificate.pem")
KEY_FILE = os.path.join(CERT_DIR, "private-key.pem")

# Проверка и создание директории для сертификатов
if not os.path.exists(CERT_DIR):
    os.makedirs(CERT_DIR)
    print(f"Директория {CERT_DIR} создана")

# Проверка наличия сертификатов и ключей
if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
    print("Сертификаты или ключи не найдены. Генерация...")

    # Параметры для сертификата (можно настроить под себя)
    subject = "/C=US/ST=California/L=San Francisco/O=MyOrg/OU=MyUnit/CN=localhost"

    # Генерация сертификатов и ключей с помощью OpenSSL
    result = subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", KEY_FILE, "-out", CERT_FILE, "-days", "365", "-nodes",
            "-subj", subject  # Указываем все параметры в одном месте
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Выводим стандартный вывод и ошибки
    print(f"stdout: {result.stdout.decode()}")
    print(f"stderr: {result.stderr.decode()}")

    # Проверка успешности генерации сертификатов
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f"Сертификат и ключ успешно созданы в {CERT_DIR}")
    else:
        print(f"Ошибка: не удалось создать сертификат или ключ.")
        exit(1)

# Настройка SSL
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)


# Обработчик WebSocket-сообщений
async def handler(websocket, path):
    # try:
    #     print(f"New connection from {websocket.remote_address}")
    #
    #     # Принимаем сообщение от клиента
    #     message = await websocket.recv()
    #     print(f"Received message: {message}")
    #
    #     # Отправляем сообщение обратно клиенту
    #     response = f"Echo: {message}"
    #     await websocket.send(response)
    #     print(f"Sent response: {response}")
    # except Exception as e:
    #     print(f"Error during communication: {e}")
    # finally:
    #     await websocket.close()
    print(f"Новое подключение: {websocket.remote_address}")
    try:
        while True:
            # Получаем сообщение от клиента
            message = await websocket.recv()
            print(f"Получено сообщение от клиента: {message}")

            # Отправляем сообщение обратно клиенту
            response = f"Echo: {message}"
            await websocket.send(response)
            print(f"Ответ отправлен: {response}")
    except websockets.ConnectionClosed:
        print("Соединение закрыто.")
    except Exception as e:
        print(f"Ошибка при обработке сообщений: {e}")
    finally:
        print("Обработка завершена.")


# Основная функция запуска сервера
async def main():
    print(f"Запуск сервера на {HOST}:{PORT}...")
    server = await websockets.serve(
        handler,
        HOST,
        PORT,
        ssl=ssl_context
    )
    print(f"Сервер запущен. Ожидание подключений на wss://{HOST}:{PORT}")

    # Запускаем сервер и ждем завершения
    await server.wait_closed()


# Запуск сервера
if __name__ == "__main__":
    asyncio.run(main())

    