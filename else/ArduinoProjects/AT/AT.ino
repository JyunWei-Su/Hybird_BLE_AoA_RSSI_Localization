void setup() {
// put your setup code here, to run once:
Serial.begin(115200);
Serial2.begin(115200);
}
void loop() {
// put your main code here, to run repeatedly:
if (Serial.available()){
  char temp = Serial.read();
  Serial2.write(temp);
  Serial.print("SEND: ");
  Serial.println(temp, HEX);
}
if (Serial2.available()){
  char temp = Serial2.read();
  Serial.print(temp);
  Serial.print(" (");
  Serial.print(temp, HEX);
  Serial.println(")");
}
}
