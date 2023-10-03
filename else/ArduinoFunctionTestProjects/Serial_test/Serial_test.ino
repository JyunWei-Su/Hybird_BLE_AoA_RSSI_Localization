/*
  DigitalReadSerial

  Reads a digital input on pin 2, prints the result to the Serial Monitor

  This example code is in the public domain.

  https://www.arduino.cc/en/Tutorial/BuiltInExamples/DigitalReadSerial
*/



// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  Serial.println();
  Serial.println("Stop Node-RED                       ✔");

}

// the loop routine runs over and over again forever:
void loop() {
  delay(1);        // delay in between reads for stability
  Serial.print("12345");
  delay(5000);
  Serial.print("\b\b\b789\r\n");
}
