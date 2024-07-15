#include <SDI12.h>
#define SERIAL_BAUD 115200
#define DATA_PIN 2
#define MAX_CMD_LENGTH 10
#define LED_PIN 13

SDI12 mySDI12(DATA_PIN);
char cmd[MAX_CMD_LENGTH + 1]; // Buffer to store the command including the null terminator
int cmdIndex = 0;
bool ledState = false; // Variable to track LED state

void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial);
  pinMode(LED_PIN, OUTPUT); 

  // Initiate serial connection to SDI-12 bus
  mySDI12.begin();
  delay(10);
  mySDI12.forceListen();
}

void loop() {
  // Read the command from the serial input
  char serialMsgChar = '\0';
  while (Serial.available()) {
    serialMsgChar = Serial.read();
    
    // If newline or carriage return is received, send the command
    if (serialMsgChar == '\n' || serialMsgChar == '\r') {
      cmd[cmdIndex] = '\0'; // Null-terminate the command
      mySDI12.sendCommand(cmd);
      cmdIndex = 0; // Reset the command index for the next command
      ledState = !ledState;
      //digitalWrite(LED_PIN, ledState ? HIGH : LOW); //can be used for debug
    } else {
      if (cmdIndex < MAX_CMD_LENGTH) {
        cmd[cmdIndex++] = serialMsgChar;
      }
    }
  }

  // Read the response from the SDI-12 sensor
  int avail = mySDI12.available();
  if (avail < 0) {
    mySDI12.clearBuffer();
  } else if (avail > 0) {
    for (int a = 0; a < avail; a++) {
      char inByte = mySDI12.read();
      Serial.write(inByte);
    }
  }
}
