import socket
import time
import json
from kuksa_client.grpc import VSSClient, Datapoint

# --- UDP Receiver Setup ---
X8_IP = "192.168.1.60"
X8_RX_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((X8_IP, X8_RX_PORT))

print("X8 UDP ready.")

# --- Kuksa Client Setup ---
with VSSClient('127.0.0.1', 55555) as client:
    while True:
        sock.settimeout(1.0)
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()

            # Try parsing JSON
            try:
                msg_dict = json.loads(message)

                # Handle multiple messages in an array
                if isinstance(msg_dict, list):
                    for item in msg_dict:
                        signal = item.get("signal")
                        value = item.get("value")
                        if signal and value is not None:
                            # Send to Kuksa
                            client.set_current_values({signal: Datapoint(value)})
                            print(f"Sent to Kuksa -> {signal}: {value}")
                else:
                    signal = msg_dict.get("signal")
                    value = msg_dict.get("value")
                    if signal and value is not None:
                        # Send to Kuksa
                        client.set_current_values({signal: Datapoint(value)})
                        print(f"Sent to Kuksa -> {signal}: {value}")

            except json.JSONDecodeError:
                print("Received non-JSON data:", message)

        except socket.timeout:
            pass

        time.sleep(0.1)
