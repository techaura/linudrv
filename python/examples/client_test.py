import asyncio
import ssl
import websockets

URI = "wss://localhost:8765"
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def send_messages(websocket, stop_event):
    try:
        while not stop_event.is_set():
            message = input("Введите сообщение для отправки ('exit' для завершения): ")
            if message.lower() == "exit":
                stop_event.set()
                await websocket.close()
                break
            await websocket.send(message)
            print(f"Отправлено: {message}")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

async def receive_messages(websocket, stop_event):
    try:
        while not stop_event.is_set():
            response = await websocket.recv()
            print(f"Получено от сервера: {response}")
    except Exception as e:
        print(f"Ошибка при получении: {e}")

async def main():
    stop_event = asyncio.Event()
    async with websockets.connect(URI, ssl=ssl_context) as websocket:
        send_task = asyncio.create_task(send_messages(websocket, stop_event))
        receive_task = asyncio.create_task(receive_messages(websocket, stop_event))

        done, pending = await asyncio.wait(
            [send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        stop_event.set()
        for task in pending:
            task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
