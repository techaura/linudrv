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
async def send_messages(websocket, input_queue, exit_event):
    try:
        while not exit_event.is_set():
            message = await asyncio.to_thread(input_queue.get)
            if message.lower() == "exit":
                print("Завершение соединения...")
                await websocket.close()
                exit_event.set()
                return
            await websocket.send(message)
            print(f"Отправлено: {message}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# Асинхронная функция получения сообщений
async def receive_messages(websocket, exit_event, disconnect_event):
    try:
        while not exit_event.is_set():
            response = await websocket.recv()
            print(f"\nПолучено от сервера: {response}")
            print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
    except websockets.ConnectionClosed:
        print("\nСоединение закрыто сервером.")
        disconnect_event.set()
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")
        disconnect_event.set()

# Основная функция подключения и управления реконнектом
async def connect_to_server(input_queue, exit_event):
    disconnect_event = asyncio.Event()

    while not exit_event.is_set():
        disconnect_event.clear()  # Сброс состояния перед подключением

        try:
            print(f"\nПопытка подключения к серверу {URI}...")
            async with websockets.connect(URI, ssl=ssl_context) as websocket:
                print("Подключение установлено.")
                print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)

                # Запуск задач для отправки и получения сообщений
                await asyncio.gather(
                    send_messages(websocket, input_queue, exit_event),
                    receive_messages(websocket, exit_event, disconnect_event),
                )
        except (websockets.ConnectionClosed, ConnectionRefusedError):
            print("\nСервер недоступен.")
        except Exception as e:
            print(f"\nОшибка клиента: {e}.")
        finally:
            if exit_event.is_set():
                print("\nКлиент завершил работу.")
                break

        # Ожидание реконнекта, если соединение было потеряно
        if not disconnect_event.is_set():
            disconnect_event.set()

        print("Ожидание перед реконнектом...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    input_queue = Queue()
    exit_event = asyncio.Event()

    # Запуск потока для ввода
    input_thread_instance = Thread(target=input_thread, args=(input_queue, exit_event))
    input_thread_instance.daemon = True
    input_thread_instance.start()

    # Запуск основного цикла клиента
    asyncio.run(connect_to_server(input_queue, exit_event))
