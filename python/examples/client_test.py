import asyncio
import ssl
import websockets
from threading import Thread
from queue import Queue

# Настройки клиента
HOST = "localhost"
PORT = 8765
URI = f"wss://{HOST}:{PORT}"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Поток для ввода данных
def input_thread(input_queue):
    while True:
        print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
        message = input()
        input_queue.put(message)
        if message.lower() == "exit":
            break

# Асинхронная функция отправки сообщений
async def send_messages(websocket, input_queue):
    try:
        while True:
            message = await asyncio.to_thread(input_queue.get)
            if message.lower() == "exit":
                print("Завершение соединения...")
                await websocket.close()
                break
            await websocket.send(message)
            print(f"Отправлено: {message}")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

# Асинхронная функция получения сообщений
async def receive_messages(websocket):
    try:
        while True:
            response = await websocket.recv()
            print(f"\nПолучено от сервера: {response}")
            print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
    except websockets.ConnectionClosedOK:
        print("Соединение закрыто (получение).")
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")

# Основная функция клиента
async def test_client():
    input_queue = Queue()

    # Запуск потока для ввода
    input_thread_instance = Thread(target=input_thread, args=(input_queue,))
    input_thread_instance.daemon = True
    input_thread_instance.start()

    try:
        print(f"Подключение к серверу {URI}...")
        async with websockets.connect(URI, ssl=ssl_context) as websocket:
            print("Подключение установлено.")
            # Первое приглашение для ввода
            print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)

            # Запуск задач для отправки и получения сообщений
            await asyncio.gather(
                send_messages(websocket, input_queue),
                receive_messages(websocket),
            )
    except Exception as e:
        print(f"Ошибка клиента: {e}")
        import traceback
        traceback.print_exc()

# Запуск клиента
if __name__ == "__main__":
    asyncio.run(test_client())
