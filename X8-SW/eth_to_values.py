import socket
import time
import json

X8_IP = "192.168.1.60"
X8_RX_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((X8_IP, X8_RX_PORT))

print("X8 UDP ready.")

while True:
    sock.settimeout(1.0)
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()

        # Try to parse JSON
        try:
            msg_dict = json.loads(message)
            # If multiple messages in a string (like '[{},{}]'), handle them
            if isinstance(msg_dict, list):
                for item in msg_dict:
                    signal = item.get("signal", "N/A")
                    value = item.get("value", "N/A")
                    print(f"Signal: {signal}, Value: {value}")
            else:
                signal = msg_dict.get("signal", "N/A")
                value = msg_dict.get("value", "N/A")
                print(f"Signal: {signal}, Value: {value}")
        except json.JSONDecodeError:
            print("Received non-JSON data:", message)

    except socket.timeout:
        pass

    time.sleep(0.1)  # slightly faster loop
