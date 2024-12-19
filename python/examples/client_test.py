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
def input_thread(input_queue, stop_event):
    while not stop_event.is_set():
        print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
        message = input()
        input_queue.put(message)
        if message.lower() == "exit":
            stop_event.set()
            break

# Асинхронная функция отправки сообщений
async def send_messages(websocket, input_queue, stop_event):
    try:
        while not stop_event.is_set():
            # Ожидание сообщения от пользователя
            message = await asyncio.to_thread(input_queue.get)
            if message.lower() == "exit":
                print("Завершение соединения...")
                await websocket.close()
                stop_event.set()
                break
            if websocket.open:
                await websocket.send(message)
                print(f"Отправлено: {message}")
            else:
                print("Соединение отсутствует. Сообщение не отправлено.")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

# Асинхронная функция получения сообщений
async def receive_messages(websocket, stop_event):
    try:
        while not stop_event.is_set():
            try:
                response = await websocket.recv()
                print(f"\nПолучено от сервера: {response}")
                print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)
            except websockets.ConnectionClosed:
                print("\nСоединение закрыто сервером.")
                stop_event.set()
                break
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")

# Основная функция клиента
async def test_client():
    input_queue = Queue()
    stop_event = asyncio.Event()

    # Запуск потока для ввода
    input_thread_instance = Thread(target=input_thread, args=(input_queue, stop_event))
    input_thread_instance.daemon = True
    input_thread_instance.start()

    while not stop_event.is_set():
        try:
            print(f"\nПопытка подключения к серверу {URI}...")
            async with websockets.connect(URI, ssl=ssl_context) as websocket:
                print("Подключение установлено.")
                print("Введите сообщение для отправки ('exit' для завершения):", end=" ", flush=True)

                # Запуск задач для отправки и получения сообщений
                await asyncio.gather(
                    send_messages(websocket, input_queue, stop_event),
                    receive_messages(websocket, stop_event),
                )
        except websockets.ConnectionClosed:
            print("\nСоединение с сервером потеряно. Повторная попытка через 5 секунд...")
        except Exception as e:
            print(f"\nОшибка клиента: {e}. Повторная попытка через 5 секунд...")
        finally:
            if stop_event.is_set():
                print("\nКлиент завершил работу.")
                break

        # Ожидание перед повторной попыткой подключения
        for i in range(5, 0, -1):
            print(f"\rПереподключение через {i} секунд...", end="", flush=True)
            await asyncio.sleep(1)
        print("\nПопытка подключения снова.")

if __name__ == "__main__":
    asyncio.run(test_client())
