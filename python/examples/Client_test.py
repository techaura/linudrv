import asyncio
import ssl
import websockets

# Настройки клиента
HOST = "localhost"  # Замените на IP-адрес сервера
PORT = 8765
URI = f"wss://{HOST}:{PORT}"  # URL для подключения к серверу

# SSL-контекст для защиты соединения
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False  # Отключаем проверку имени хоста
ssl_context.verify_mode = ssl.CERT_NONE  # Отключаем проверку сертификата (только для тестов!)


# Функция отправки сообщений
async def send_messages(websocket):
    try:
        while True:
            message = input("Введите сообщение для отправки: ")
            if message.lower() == "exit":
                print("Завершение соединения...")
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
    print("Получение сообщений запущено")
    try:
        while True:
            response = await websocket.recv()
            print(f"Получено сообщение от сервера: {response}")
    except websockets.ConnectionClosedOK:
        print("Соединение закрыто (получение).")
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")


# Основная клиентская функция
async def test_client():
    try:
        async with websockets.connect(URI, ssl=ssl_context) as websocket:
            print("Подключение установлено. Введите 'exit' для завершения.")

            # Запуск задач для отправки и получения сообщений
            send_task = asyncio.create_task(send_messages(websocket))
            receive_task = asyncio.create_task(receive_messages(websocket))

            # Ожидание завершения задач
            done, pending = await asyncio.wait(
                [send_task, receive_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Отмена оставшихся задач
            for task in pending:
                task.cancel()
    except Exception as e:
        print(f"Ошибка: {e}")

# Запуск клиента
if __name__ == "__main__":
    asyncio.run(test_client())

