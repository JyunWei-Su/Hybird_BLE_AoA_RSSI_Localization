//#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <WiFi.h>
#include <ESPmDNS.h>
//#include <ESP8266mDNS.h>

//https://forum.arduino.cc/t/sending-udp-packets-from-an-esp8266-nodemcu/855730
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
char incomingByte = 0;   // for incoming serial data
int incomingCount = 0; //指向現在空的那位
static unsigned char incomingTemp[100];
WiFiUDP Udp;
IPAddress serverIp;

void setup() {
  Serial.begin(115200);
  Serial.print("\n\rAT+CPWROFF\n\r");

  
  WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  // -----mDNS
  while(mdns_init()!= ESP_OK){
    delay(1000);
    Serial.println("Starting MDNS...");
  }
 
  Serial.println("MDNS started");
  
  
 
  while (serverIp.toString() == "0.0.0.0") {
    Serial.println("Resolving host...");
    delay(250);
    serverIp = MDNS.queryHost("raspberrypi-test");
  }
 
  Serial.println("Host address resolved:");
  Serial.println(serverIp.toString());
  //-----
  char temp2[20];
  sprintf(temp2, "ok!");
  Udp.beginPacket(serverIp.toString().c_str(), 4101);
    //Udp.write("ok!");
    Udp.write((const uint8_t *)temp2, sizeof(temp2));
    Udp.endPacket();

    
}

void loop() {
 // Udp.beginPacket("192.168.98.65", 4101);
 
 //sprintf(temp, "%anchor_1:%08d", millis());
 //sprintf(temp, "%anchor_2:%08d", millis());

  if (Serial.available() > 0) {
    Serial.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
    if(incomingTemp[0] == '+'){
      //Udp.beginPacket("192.168.51.191", 4101);
      Udp.beginPacket(serverIp.toString().c_str(), 4101);
      //sprintf(temp, "%c(%03d)", incomingByte, (int)incomingByte);
      Udp.write(incomingTemp, sizeof(incomingTemp));
      Udp.endPacket();
    }
  }
}
