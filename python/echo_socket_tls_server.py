import asyncio
import websockets
import ssl
import os
import subprocess

# Settings
HOST = "localhost"
PORT = 8765
CERT_DIR = "misc"
CERT_FILE = os.path.join(CERT_DIR, "certificate.pem")
KEY_FILE = os.path.join(CERT_DIR, "private-key.pem")

# Checking and creating a directory for certificates
try:
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)
        print(f"Directory {CERT_DIR} has been created")
except PermissionError:
    print(f"Permission denied: Unable to create directory {CERT_DIR}. Please check your access rights.")
    exit(1)
except FileExistsError:
    print(f"Failed to create directory {CERT_DIR}: A file with the same name already exists.")
    exit(1)
except OSError as e:
    print(f"OS error occurred while creating directory {CERT_DIR}: {e}")
    exit(1)

# Checking the availability of certificates and keys
if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
    print("Сертификаты или ключи не найдены. Генерация...")

    # Parameters for the certificate (can be customized)
    subject = "/C=US/ST=California/L=San Francisco/O=MyOrg/OU=MyUnit/CN=localhost"

    # Certificate and key generation with OpenSSL
    result = subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", KEY_FILE, "-out", CERT_FILE, "-days", "365", "-nodes",
            "-subj", subject  # Указываем все параметры в одном месте
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Output standard output and errors
    print(f"stdout: {result.stdout.decode()}")
    print(f"stderr: {result.stderr.decode()}")

    # Checking the success of certificate generation
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f"Сертификат и ключ успешно созданы в {CERT_DIR}")
    else:
        print(f"Ошибка: не удалось создать сертификат или ключ.")
        exit(1)

# SSL Configuration
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)


# WebSocket message handler
async def handler(websocket, path):
    print(f"Новое подключение: {websocket.remote_address}")
    try:
        while True:
            message = await websocket.recv()
            print(f"Получено сообщение от клиента: {message}")
            response = f"Echo: {message}"
            await websocket.send(response)
            print(f"Ответ отправлен: {response}")
    except websockets.ConnectionClosed:
        print("Соединение закрыто.")
    except Exception as e:
        print(f"Ошибка при обработке сообщений: {e}")
    finally:
        print("Обработка завершена.")


# Basic server startup function
async def main():
    print(f"Запуск сервера на {HOST}:{PORT}...")
    server = await websockets.serve(
        handler,
        HOST,
        PORT,
        ssl=ssl_context
    )
    print(f"Сервер запущен. Ожидание подключений на wss://{HOST}:{PORT}")

    # Start the server and wait for it to finish
    await server.wait_closed()
