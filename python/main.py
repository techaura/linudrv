import asyncio
import websockets
import ssl
import os
import subprocess
import psutil

# Settings
HOST = "0.0.0.0"
PORT = 8765
CERT_DIR = "misc"
CERT_FILE = os.path.join(CERT_DIR, "certificate.pem")
KEY_FILE = os.path.join(CERT_DIR, "private-key.pem")

# Checking and creating a directory for certificates
try:
    if not os.path.exists(CERT_DIR):
        os.makedirs(CERT_DIR)
        print(f"Directory {CERT_DIR} has been created")
except PermissionError:
    print(f"Permission denied: Unable to create directory {CERT_DIR}. Please check your access rights.")
    exit(1)
except FileExistsError:
    print(f"Failed to create directory {CERT_DIR}: A file with the same name already exists.")
    exit(1)
except OSError as e:
    print(f"OS error occurred while creating directory {CERT_DIR}: {e}")
    exit(1)

# Checking the availability of certificates and keys
if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
    print("No certificates or keys found. Auto generation...")

    # Parameters for the certificate (can be customized)
    subject = "/C=US/ST=California/L=San Francisco/O=MyOrg/OU=MyUnit/CN=localhost"

    # Certificate and key generation with OpenSSL
    result = subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", KEY_FILE, "-out", CERT_FILE, "-days", "365", "-nodes",
            "-subj", subject  # Specify all parameters in one place
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Output standard output and errors
    print(f"stdout: {result.stdout.decode()}")
    print(f"stderr: {result.stderr.decode()}")

    # Checking the success of certificate generation
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f"The certificate and key were successfully created in {CERT_DIR}")
    else:
        print(f"Error: Failed to create certificate or key.")
        exit(1)

# SSL Configuration
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)


# WebSocket message handler
async def handler(websocket, path):
    print(f"New connection: {websocket.remote_address}")

    # Get memory usage information and log it
    process = psutil.Process()
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Memory usage in MB
    print(f"Current server memory usage: {memory_usage:.2f} MB (after new connection)")

    try:
        while True:
            message = await websocket.recv()
            print(f"Message received from the client: {message}")
            response = f"Echo: {message}"
            await websocket.send(response)
            print(f"Response sent: {response}")
    except websockets.ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"Error during message processing: {e}")
    finally:
        print("Processing complete.")


# Basic server startup function
async def main():
    print(f"Running the server on {HOST}:{PORT}...")
    server = await websockets.serve(
        handler,
        HOST,
        PORT,
        ssl=ssl_context
    )
    print(f"The server is up and running. Waiting for connections on wss://{HOST}:{PORT}")

    # Start the server and wait for it to finish
    await server.wait_closed()


# Server startup
if __name__ == "__main__":
    asyncio.run(main())

    