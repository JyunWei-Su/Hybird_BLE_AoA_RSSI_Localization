#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
//https://forum.arduino.cc/t/sending-udp-packets-from-an-esp8266-nodemcu/855730
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
WiFiUDP Udp;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
}

void loop() {
 delay(10);
 Udp.beginPacket("192.168.98.65", 4101);
 static char temp[20];
 sprintf(temp, "%anchor_1:%08d", millis());
 //sprintf(temp, "%anchor_2:%08d", millis());
 Udp.write(temp);
 Udp.endPacket();
 delay(20);
}
