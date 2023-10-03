#if defined(ESP8266)
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#define CLIENT_NAME "nodemcu"
#elif defined(ESP32)
#include <WiFi.h>
#include <ESPmDNS.h>
#define CLIENT_NAME "nodemcu32s"
#else
#error This code only support ESP8266, ESP32.
#endif

#define HOST_NAME   "raspberrypi-test"
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
static unsigned char incomingTemp[100];
WiFiUDP Udp;
IPAddress serverIp;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);
  Serial2.begin(115200);
  Serial2.print("\r");
  Serial2.flush();
  Serial2.print("AT+CPWROFF\r");
  Serial2.flush();
  Serial.println();
  Serial.print("Connecting to WiFi..");
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(CLIENT_NAME);
  WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.print("connected: ");
  Serial.println(WiFi.localIP().toString() + " RSSI:" + (String)WiFi.RSSI());
  
  // -----mDNS
  Serial.print("Starting MDNS..");
  if(!MDNS.begin(CLIENT_NAME)) {
     Serial.println("Error starting mDNS");
  }else{
  MDNS.addService("http", "tcp", 80);
  Serial.println("started");
  }
  Serial.print("Resolving host..");
  while (serverIp.toString() == "0.0.0.0") { //(IP unset)
    delay(250);
    Serial.print(".");
    serverIp = MDNS.queryHost(HOST_NAME);
  }
  Serial.print("resolved: ");
  Serial.println(serverIp.toString());
  
  //-----

  Udp.beginPacket(serverIp.toString().c_str(), 4101);
  Udp.write((const uint8_t *)"ok!", sizeof("ok!"));
  Udp.endPacket();
  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
  if(Serial2.available() > 0) {
    Serial2.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
    if(incomingTemp[0] == '+'){
      Udp.beginPacket(serverIp.toString().c_str(), 4101);
      Udp.write(incomingTemp, sizeof(incomingTemp));
      Udp.endPacket();
    }
  }
}
