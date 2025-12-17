import socket
import time
import json
import threading

from kuksa_client.grpc import VSSClient, Datapoint

# ============================================================
# UDP CONFIG
# ============================================================
X8_IP = "192.168.1.60"
X8_RX_PORT = 5005

H7_IP = "192.168.1.50"
H7_RX_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((X8_IP, X8_RX_PORT))
sock.settimeout(0.1)

print("X8 UDP ready.")

# ============================================================
# SHARED STATE
# ============================================================
subscribed_signals = set()      # All detected signals
last_forwarded = {}             # signal -> last value forwarded
subscription_version = 0        # Increment when signal list changes
state_lock = threading.Lock()


# ============================================================
# UDP SEND (X8 -> H7)
# ============================================================
def send_udp(signal, value):
    msg = json.dumps({
        "signal": signal,
        "value": value
    })
    sock.sendto(msg.encode(), (H7_IP, H7_RX_PORT))
    print(f"Kuksa  UDP: {signal} = {value}")


# ============================================================
# KUKSA SUBSCRIPTION THREAD
# ============================================================
def kuksa_subscriber():
    with VSSClient('127.0.0.1', 55555) as client:
        local_version = -1

        while True:
            with state_lock:
                if subscription_version == local_version:
                    signals = None
                else:
                    signals = list(subscribed_signals)
                    local_version = subscription_version

            if not signals:
                time.sleep(0.2)
                continue

            print(f"Subscribing to: {signals}")

            try:
                for updates in client.subscribe_current_values(signals):

                    # ?? If signal list changed  resubscribe
                    with state_lock:
                        if local_version != subscription_version:
                            print("Signal list changed  resubscribing")
                            break

                    for signal, datapoint in updates.items():
                        value = datapoint.value

                        with state_lock:
                            # Prevent echo loop
                            if last_forwarded.get(signal) == value:
                                continue
                            last_forwarded[signal] = value

                        send_udp(signal, value)

            except Exception as e:
                print("Subscription error:", e)
                time.sleep(1)


# ============================================================
# START SUBSCRIPTION THREAD
# ============================================================
threading.Thread(
    target=kuksa_subscriber,
    daemon=True
).start()


# ============================================================
# MAIN LOOP: UDP  KUKSA
# ============================================================
with VSSClient('127.0.0.1', 55555) as client:
    while True:
        try:
            data, addr = sock.recvfrom(2048)
            message = data.decode().strip()

            try:
                msg = json.loads(message)
                items = msg if isinstance(msg, list) else [msg]

                for item in items:
                    signal = item.get("signal")
                    value = item.get("value")

                    if not signal or value is None:
                        continue

                    # Send to Kuksa
                    client.set_current_values({
                        signal: Datapoint(value)
                    })
                    print(f"UDP  Kuksa: {signal} = {value}")

                    # Track signal + trigger resubscribe if new
                    with state_lock:
                        if signal not in subscribed_signals:
                            subscribed_signals.add(signal)
                            subscription_version += 1   # ?? trigger resubscribe

                        last_forwarded[signal] = value

            except json.JSONDecodeError:
                print("Received non-JSON:", message)

        except socket.timeout:
            pass

        time.sleep(0.05)