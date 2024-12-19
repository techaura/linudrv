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
def input_thread(input_queue, exit_event):
    while not exit_event.is_set():
        print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
        message = input()
        input_queue.put(message)
        if message.lower() == "exit":
            exit_event.set()
            break

# Асинхронная функция отправки сообщений
async def send_messages(websocket, input_queue):
    while True:
        try:
            message = await asyncio.to_thread(input_queue.get)
            if message.lower() == "exit":
                print("Завершение соединения...")
                await websocket.close()
                return
            await websocket.send(message)
            print(f"Отправлено: {message}")
        except websockets.ConnectionClosed:
            print("Соединение отсутствует. Сообщение не отправлено.")
            await asyncio.sleep(1)  # Немного подождать перед повтором
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            return

# Асинхронная функция получения сообщений
async def receive_messages(websocket):
    while True:
        try:
            response = await websocket.recv()
            print(f"\nПолучено от сервера: {response}")
            print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
        except websockets.ConnectionClosed:
            print("\nСоединение закрыто сервером.")
            return
        except Exception as e:
            print(f"Ошибка при получении сообщения: {e}")
            return

# Основная функция клиента
async def connect_to_server(input_queue, exit_event):
    while not exit_event.is_set():
        try:
            print(f"\nПопытка подключения к серверу {URI}...")
            async with websockets.connect(URI, ssl=ssl_context) as websocket:
                print("Подключение установлено.")
                print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)

                # Запуск задач для отправки и получения сообщений
                await asyncio.gather(
                    send_messages(websocket, input_queue),
                    receive_messages(websocket),
                )
        except (websockets.ConnectionClosed, ConnectionRefusedError):
            print("\nСервер недоступен. Повторная попытка через 5 секунд...")
        except Exception as e:
            print(f"\nОшибка клиента: {e}. Повторная попытка через 5 секунд...")
        finally:
            await asyncio.sleep(5)  # Ожидание перед повторной попыткой подключения

    print("\nКлиент завершил работу.")

if __name__ == "__main__":
    input_queue = Queue()
    exit_event = asyncio.Event()

    # Запуск потока для ввода
    input_thread_instance = Thread(target=input_thread, args=(input_queue, exit_event))
    input_thread_instance.daemon = True
    input_thread_instance.start()

    # Запуск основного цикла клиента
    asyncio.run(connect_to_server(input_queue, exit_event))
