import asyncio
import ssl
import websockets
from threading import Thread
from queue import Queue

# Client setup
HOST = "192.168.88.245"
PORT = 8765
URI = f"wss://{HOST}:{PORT}"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


# user input data thread
def input_thread(input_queue, exit_event):
    while not exit_event.is_set():
        print("Enter the message to send ('exit' to finish):", end=" ", flush=True)
        message = input()
        input_queue.put(message)
        if message.lower() == "exit":
            exit_event.set()
            break


# Async message send
async def send_messages(websocket, input_queue, exit_event):
    try:
        while not exit_event.is_set():
            message = await asyncio.to_thread(input_queue.get)
            if message.lower() == "exit":
                print("Ending the connection...")
                await websocket.close()
                exit_event.set()
                return
            await websocket.send(message)
            print(f"Posted in: {message}")
    except Exception as e:
        print(f"Error when sending a message: {e}")


# Async message received
async def receive_messages(websocket, exit_event, connection_event):
    try:
        while not exit_event.is_set():
            response = await websocket.recv()
            print(f"\nReceived from the server: {response}")
            print("Enter the message to send ('exit' to finish):", end=" ", flush=True)
    except websockets.ConnectionClosed:
        print("\nConnection closed by the server.")
        connection_event.clear()
    except Exception as e:
        print(f"Error when receiving a message: {e}")
        connection_event.clear()


# Reconnection timer
async def reconnect_timer(input_queue, exit_event, connection_event):
    while not exit_event.is_set():
        await asyncio.sleep(5)  # time in seconds before try to next reconnect
        if not connection_event.is_set():
            print("\nReconnection attempt...")
            await connect_to_server(input_queue, exit_event, connection_event)


# Connect to server function
async def connect_to_server(input_queue, exit_event, connection_event):
    try:
        print(f"\nattempt to connect to the server {URI}...")
        async with websockets.connect(URI, ssl=ssl_context) as websocket:
            print("Connection established.")
            print("Enter the message to be sent ('exit' to close client):", end=" ", flush=True)
            connection_event.set()  # Установить состояние соединения

            # Запуск задач для отправки и получения сообщений
            await asyncio.gather(
                send_messages(websocket, input_queue, exit_event),
                receive_messages(websocket, exit_event, connection_event),
            )
    except (websockets.ConnectionClosed, ConnectionRefusedError):
        print("\nserver is unavailable.")
        connection_event.clear()
    except Exception as e:
        print(f"\nClienr ERROR: {e}.")
        connection_event.clear()



async def main():
    input_queue = Queue()
    exit_event = asyncio.Event()
    connection_event = asyncio.Event()  # connection flag

    # start user input task
    input_thread_instance = Thread(target=input_thread, args=(input_queue, exit_event))
    input_thread_instance.daemon = True
    input_thread_instance.start()

    # All task start
    await asyncio.gather(
        reconnect_timer(input_queue, exit_event, connection_event),
        connect_to_server(input_queue, exit_event, connection_event),
    )

if __name__ == "__main__":
    asyncio.run(main())
