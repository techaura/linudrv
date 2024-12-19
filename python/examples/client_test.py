import asyncio
import ssl
import websockets
from threading import Thread
from queue import Queue, Empty

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
async def send_messages(websocket, input_queue, stop_event):
    try:
        while not stop_event.is_set():
            try:
                message = input_queue.get_nowait()
            except Empty:
                await asyncio.sleep(0.1)
                continue

            if message.lower() == "exit":
                print("Завершение соединения...")
                await websocket.close()
                stop_event.set()
                break
            await websocket.send(message)
            print(f"Отправлено: {message}")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

# Асинхронная функция получения сообщений
async def receive_messages(websocket, stop_event):
    try:
        while not stop_event.is_set():
            try:
                response = await websocket.recv()
                print(f"\nПолучено от сервера: {response}")
            except websockets.ConnectionClosedOK:
                print("\nСоединение закрыто сервером.")
                stop_event.set()
                break
            except websockets.ConnectionClosedError as e:
                print(f"\nОшибка соединения: {e}")
                stop_event.set()
                break
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")

# Функция переподключения
async def reconnect(input_queue):
    stop_event = asyncio.Event()
    while True:
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
        except Exception as e:
            print(f"\nОшибка подключения: {e}. Повторная попытка через 5 секунд...")
            for i in range(5, 0, -1):
                print(f"\rПереподключение через {i} секунд...", end="", flush=True)
                await asyncio.sleep(1)
            print("\nПопытка подключения снова.")
        finally:
            if stop_event.is_set():
                print("\nКлиент завершил работу.")
                break

# Основная функция клиента
def main():
    input_queue = Queue()

    # Запуск потока для ввода
    input_thread_instance = Thread(target=input_thread, args=(input_queue,))
    input_thread_instance.daemon = True
    input_thread_instance.start()

    asyncio.run(reconnect(input_queue))

if __name__ == "__main__":
    main()
