#include <Ethernet.h>
#include <ArduinoJson.h>
#include <EthernetUdp.h>

// ----------------------
// NETWORK CONFIG
// ----------------------
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress localIP(192, 168, 1, 50);  // H7 static IP
IPAddress x8IP(192, 168, 1, 60);     // X8 static IP
const uint16_t x8Port = 5005;        // X8 listening port
const uint16_t h7Port = 5006;        // H7 receive port

EthernetUDP Udp;

// ----------------------
// VSS Values (known signals)
// ----------------------
int vehicleSpeed;
int row1DriverTemp;
int row2DriverTemp;

// ----------------------
// Send JSON via UDP
// ----------------------
void sendVSS(const char* signalName, int value) {
  StaticJsonDocument<128> doc;
  doc["signal"] = signalName;
  doc["value"] = value;

  char buffer[128];
  size_t len = serializeJson(doc, buffer);

  Udp.beginPacket(x8IP, x8Port);
  Udp.write((uint8_t*)buffer, len);
  Udp.endPacket();

  Serial.print("Sent → ");
  Serial.println(buffer);
}

// ----------------------
// Receive UDP messages from X8
// ----------------------
void receiveFromX8() {
  int packetSize = Udp.parsePacket();
  if (!packetSize) return;

  char buffer[256];
  int len = Udp.read(buffer, sizeof(buffer) - 1);
  buffer[len] = '\0';

  // Print exactly what we received
  Serial.print("Received → ");
  Serial.println(buffer);

  StaticJsonDocument<256> doc;
  if (deserializeJson(doc, buffer) != DeserializationError::Ok) return;

  const char* signal = doc["signal"];
  int value = doc["value"];

  // Update only known signals
  if (strcmp(signal, "Vehicle.Speed") == 0) {
    vehicleSpeed = value;
  }
  else if (strcmp(signal, "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature") == 0) {
    row1DriverTemp = value;
  }
  else if (strcmp(signal, "Vehicle.Cabin.HVAC.Station.Row2.Driver.Temperature") == 0) {
    row2DriverTemp = value;
  }
  else {
    // Unknown signal → ignore
    return;
  }

  // Confirm update
  Serial.print("Updated → ");
  Serial.print(signal);
  Serial.print(" = ");
  Serial.println(value);
}

// ----------------------
// SETUP
// ----------------------
void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("=== Portenta H7 UDP VSS (Send Once, Then Listen) ===");

  Ethernet.begin(mac, localIP);
  delay(1000);

  Udp.begin(h7Port);

  Serial.print("H7 IP: ");
  Serial.println(Ethernet.localIP());

  // Seed random
  randomSeed(millis());

  // ----------------------
  // SEND RANDOM VALUES ONCE
  // ----------------------
  vehicleSpeed = random(0, 120);
  row1DriverTemp = random(16, 30);
  row2DriverTemp = random(16, 30);

  sendVSS("Vehicle.Speed", vehicleSpeed);
  delay(50);
  sendVSS("Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature", row1DriverTemp);
  delay(50);
  sendVSS("Vehicle.Cabin.HVAC.Station.Row2.Driver.Temperature", row2DriverTemp);
  delay(50);
  Serial.println("Initial random values sent.\nListening for updates...");
}

// ----------------------
// LOOP
// ----------------------
void loop() {
  receiveFromX8();
}
