import socket
import json

# ------------------------------
# NETWORK CONFIG
# ------------------------------
X8_IP = "192.168.1.60"  # X8 static IP
X8_PORT = 5000           # same as H7 client connects to
BUFFER_SIZE = 1024

# ------------------------------
# SETUP UDP SOCKET
# ------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((X8_IP, X8_PORT))

print(f"[X8] Listening for H7 signals on {X8_IP}:{X8_PORT} ...")

# ------------------------------
# RECEIVE LOOP
# ------------------------------
while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    msg = data.decode().strip()

    try:
        json_data = json.loads(msg)
        signal = json_data.get("signal")
        value = json_data.get("value")
        print(f"[H7  X8] {signal} = {value}")
    except json.JSONDecodeError:
        print(f"[X8] Failed to parse JSON: {msg}")

