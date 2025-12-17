// This code is teseted on H7 with CAn write from CAN exaples on UNO R4

#include <Arduino_CAN.h>

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!CAN.begin(CanBitRate::BR_250k)) {
    Serial.println("CAN.begin(...) failed");
    while (1);
  }

  Serial.println("Portenta H7 listening on CAN (250 kbps)");
}

void loop() {
  if (CAN.available()) {
    CanMsg msg = CAN.read();
    Serial.print("Received ID: 0x");
    Serial.print(msg.id, HEX);
    Serial.print(" Data: ");
    for (int i = 0; i < msg.data_length; i++) {
      Serial.print(msg.data[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
  }
}
