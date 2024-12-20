import threading
import argparse
import asyncio
import time
from client_test import main as client_main  # Assuming your client_test.py has an async main() function

# Global event to signal clients to stop
stop_event = threading.Event()

# Function to run a client
def run_client(client_id):
    print(f"Starting client {client_id}")
    try:
        asyncio.run(client_main_with_stop(client_id))
    except asyncio.CancelledError:
        print(f"Client {client_id} was stopped.")
    except Exception as e:
        print(f"Error in client {client_id}: {e}")
    print(f"Client {client_id} finished")

# Wrapper for client_main to support stop event
async def client_main_with_stop(client_id):
    # Wrap the client_main in a try/finally to ensure proper exit
    task = asyncio.create_task(client_main())
    try:
        while not stop_event.is_set():
            await asyncio.sleep(1)  # Prevent tight loop
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print(f"Client {client_id} received cancel signal.")

# Main script
if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Launch multiple WebSocket clients using threads.")
    parser.add_argument("-n", "--num-clients", type=int, required=True,
                        help="Number of clients to launch.")
    args = parser.parse_args()
    num_clients = args.num_clients

    # Create and start threads
    threads = []
    print(f"Launching {num_clients} clients...")
    for i in range(num_clients):
        thread = threading.Thread(target=run_client, args=(i + 1,), daemon=True)  # Mark threads as daemons
        thread.start()
        threads.append(thread)

    # Wait for 10 seconds
    print("All clients launched. Waiting for 10 seconds...")
    time.sleep(10)

    # Signal all clients to stop
    print("Signaling clients to shut down...")
    stop_event.set()

    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=1)  # Add timeout to avoid infinite waiting

    print("All clients have been shut down.")
    print("Cleaning up asyncio event loop...")

    # Explicitly clean up the asyncio event loop
    try:
        asyncio.get_event_loop().close()
    except RuntimeError:
        pass

    print("Script completed successfully.")

