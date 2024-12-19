import asyncio
import ssl
import websockets

# Настройки клиента
HOST = "localhost"  # Замените на IP-адрес сервера
PORT = 8765
URI = f"wss://{HOST}:{PORT}"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


# Основная функция тестового клиента
async def test_client():
    try:
        print(f"Подключение к серверу {URI}...")
        async with websockets.connect(URI, ssl=ssl_context) as websocket:
            print("Подключение установлено. Введите сообщение ('exit' для завершения).")
            while True:
                message = input("Введите сообщение для отправки: ")
                if message.lower() == "exit":
                    print("Завершение соединения...")
                    await websocket.close()
                    break
                await websocket.send(message)
                print(f"Отправлено: {message}")

                response = await websocket.recv()
                print(f"Получено от сервера: {response}")
    except Exception as e:
        print(f"Ошибка клиента: {e}")
        import traceback
        traceback.print_exc()


# Запуск клиента
if __name__ == "__main__":
    asyncio.run(test_client())
    