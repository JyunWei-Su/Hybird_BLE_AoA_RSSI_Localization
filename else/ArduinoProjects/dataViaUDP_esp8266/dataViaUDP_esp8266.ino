/**
 * Demo：
 *    演示ESP8266 mDNS responder功能
 * @author 
 * @date 
 */

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <mDNSResolver.h>
#elif defined(ESP32)
#include <WiFi.h>
#include <ESPmDNS.h>
#else
#error This code only support ESP8266, ESP32.
#endif
//https://community.platformio.org/t/compile-on-both-esp32-and-esp8266/14356
#define CLIENT_NAME "nodemcu"
#define HOST_NAME   "raspberrypi-test"
//https://forum.arduino.cc/t/sending-udp-packets-from-an-esp8266-nodemcu/855730
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
static unsigned char incomingTemp[100];
WiFiUDP Udp;
IPAddress serverIp;
//using namespace mDNSResolver;
//Resolver resolver(Udp);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);
  Serial.println();
  Serial.flush();
  Serial.swap();
  //delay(500);
  Serial.print("AT+CPWROFF\r\n");
  Serial.flush();
  Serial.swap();
  //delay(500);
  Serial.println();
  Serial.print("Connecting to WiFi..");
  //WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.hostname(CLIENT_NAME);
  //WiFi.setHostname(CLIENT_NAME);
  WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("connected");
  Serial.println(WiFi.localIP().toString() + " RSSI:" + (String)WiFi.RSSI());
  
  // -----mDNS
  Serial.print("Starting MDNS..");
  //while(mdns_init()!= ESP_OK){
  //  delay(500);
  //  Serial.print(".");
  //}
  if(!MDNS.begin(CLIENT_NAME, WiFi.localIP())) {
     Serial.println("Error starting mDNS");
  }else{
    MDNS.begin(CLIENT_NAME);
    MDNS.setInstanceName(CLIENT_NAME);
    MDNS.addService("http", "tcp", 80); //https://techtutorialsx.com/2020/04/18/esp32-advertise-service-with-mdns/
    Serial.println("started");
  }
  //------
  Serial.print("Resolving host..");
  while (serverIp.toString() == "(IP unset)") {
    delay(250);
    Serial.print(".");
    // https://raspberrypi.stackexchange.com/questions/117206/reaching-my-pi-with-mdns-avahi
    // change /etc/avahi/avahi-daemon.conf
    // publish-workstation=no to publish-workstation=yes
    // sudo systemctl restart avahi-daemon.service

    for (int i = 0; i < MDNS.queryService("workstation", "tcp"); ++i) {
      //Serial.println(MDNS.hostname(i));
      if (MDNS.hostname(i).compareTo((String)HOST_NAME + (String)".local") == 0) serverIp = MDNS.IP(i);
    }
  }
  Serial.print("resolved: ");
  Serial.println(serverIp.toString());
  
  //-----

  Udp.beginPacket(serverIp.toString().c_str(), 4101);
  Udp.write((const uint8_t *)"ok!", sizeof("ok!"));
  Udp.endPacket();
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.flush();
  Serial.swap();
  //delay(500);
}

void loop() {
  MDNS.update(); //https://makesmart.net/esp8266-webserver-mit-mdns-grundgerust-tutorial/ 8266要有
  if(Serial.available() > 0) {
    Serial.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
    if(incomingTemp[0] == '+'){
      Udp.beginPacket(serverIp.toString().c_str(), 4101);
      Udp.write(incomingTemp, sizeof(incomingTemp));
      Udp.endPacket();
    }
  }
}
