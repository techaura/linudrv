import subprocess
import time

# Number of clients to launch
num_clients = 100

# Path to the client script
client_script = "client_test.py"

# List to hold subprocesses
client_processes = []

try:
    print(f"Launching {num_clients} clients...")
    for i in range(num_clients):
        # Start each client as a subprocess
        process = subprocess.Popen(["python3", client_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        client_processes.append(process)
        print(f"Client {i+1} launched.")

    print("All clients launched. Waiting for 10 seconds...")
    time.sleep(10)

except Exception as e:
    print(f"Error during client launch: {e}")

finally:
    print("Shutting down all clients...")
    for i, process in enumerate(client_processes):
        try:
            process.terminate()  # Send SIGTERM to the process
            process.wait()       # Wait for the process to terminate
            print(f"Client {i+1} shut down.")
        except Exception as e:
            print(f"Error shutting down client {i+1}: {e}")
    print("All clients have been shut down.")
