import asyncio
import ssl
import websockets

# Настройки клиента
HOST = "localhost"
PORT = 8765
URI = f"wss://{HOST}:{PORT}"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Функция отправки сообщений
async def send_messages(websocket, stop_event):
    try:
        while not stop_event.is_set():
            message = input("Введите сообщение для отправки ('exit' для завершения): ")
            if message.lower() == "exit":
                print("Завершение соединения...")
                stop_event.set()  # Сигнал для остановки всех задач
                await websocket.close()
                break
            await websocket.send(message)
            print(f"Отправлено: {message}")
    except websockets.ConnectionClosedOK:
        print("Соединение закрыто (отправка).")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# Функция получения сообщений
async def receive_messages(websocket):
    try:
        while True:
            response = await websocket.recv()
            print(f"Получено от сервера: {response}")
    except websockets.ConnectionClosedOK:
        print("Соединение закрыто (получение).")
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")

# Основная функция клиента
async def test_client():
    stop_event = asyncio.Event()  # Событие для синхронизации задач

    try:
        print(f"Подключение к серверу {URI}...")
        async with websockets.connect(URI, ssl=ssl_context) as websocket:
            print("Подключение установлено.")

            # Запуск задач отправки и получения
            send_task = asyncio.create_task(send_messages(websocket, stop_event))
            receive_task = asyncio.create_task(receive_messages(websocket, stop_event))

            print("Задачи отправки и получения запущены.")

            # Ожидание завершения одной из задач
            done, pending = await asyncio.wait(
                [send_task, receive_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Установка флага остановки для всех задач
            stop_event.set()

            # Завершение оставшихся задач
            for task in pending:
                task.cancel()
    except Exception as e:
        print(f"Ошибка клиента: {e}")
        import traceback
        traceback.print_exc()

# Запуск клиента
if __name__ == "__main__":
    asyncio.run(test_client())
