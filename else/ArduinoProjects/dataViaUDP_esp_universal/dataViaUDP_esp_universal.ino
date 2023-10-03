/**
 * @version 0.1.0
 * @author Jyun-wei, Su
 * @author Ming-Yan, Tsai
 * @date 2022/05/11
 * @brief brief description
 * @details
 * @bug esp8266 要進loop才抓的到mDNS
 * @return
 * @exception 可能拋出的異常
 * @property 屬性介紹
 * @callgraph
 * @headerfile
 * @retval
 * @see ESP32 mDNS: 
 * @see Compile on both ESP32 and ESP8266: https://community.platformio.org/t/compile-on-both-esp32-and-esp8266/14356

 * @code
 * @endcode
 * @see Reaching Pi with MDNS (Avahi): https://raspberrypi.stackexchange.com/questions/117206/reaching-my-pi-with-mdns-avahi
 * @note When ESP8266 query mDNS service on Raspberrypi, have to edit  /etc/avahi/avahi-daemon.conf on Raspberrypi
 *      publish-workstation=no to yes
 *      after than,  sudo systemctl restart avahi-daemon.service
 * @ref Coding Style and Doxygen Documentation: https://www.cs.cmu.edu/~410/doc/doxygen.html
 * @ref Doxygen style guide: http://micro-os-plus.github.io/develop/doxygen-style-guide/
  esp32 mDNS: 
  
  ??: https://swf.com.tw/?p=1525
  Send UDP Packet: https://forum.arduino.cc/t/sending-udp-packets-from-an-esp8266-nodemcu/855730
  ESP32: Query mDNS service: https://techtutorialsx.com/2020/04/27/esp32-query-mdns-service/
  ESP32: Advertise service with mDNS: https://techtutorialsx.com/2020/04/18/esp32-advertise-service-with-mdns/

 **/

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#define CLIENT_NAME "nodemcu"
#define Serial2 Serial
#elif defined(ESP32)
#include <WiFi.h>
#include <ESPmDNS.h>
#define CLIENT_NAME "nodemcu32s"
#else
#error This code only support ESP8266, ESP32 boards.
#endif

//#define HOST_NAME   "raspberrypi-test"
//const char* ssid     = "JWS_Mobile";
//const char* password = "149597870700";

#define HOST_NAME   "xplr-aoa"
const char* ssid     = "XPLR-AOA";
const char* password = "12345678";
static unsigned char incomingTemp[100];
WiFiUDP Udp;
IPAddress serverIp;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);
  
#ifdef ESP8266
  Serial.println();
  Serial.flush();
  Serial.swap();
  Serial.print("AT+CPWROFF\r");
  Serial.flush();
  Serial.swap();
#endif
#ifdef ESP32
  Serial2.begin(115200);
  Serial2.print("\r");
  Serial2.flush();
  Serial2.print("AT+CPWROFF\r");
  Serial2.flush();
#endif

  Serial.println();
  Serial.print("Connecting to WiFi..");
  
#ifdef ESP8266
  WiFi.hostname(CLIENT_NAME);
#endif
#ifdef ESP32
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(CLIENT_NAME);
#endif

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
  while ((serverIp.toString() == "(IP unset)") || (serverIp.toString() == "0.0.0.0")) {
    // (IP unset) is for esp8266, 0.0.0.0 is for esp32
    delay(250);
    Serial.print(".");
#ifdef ESP8266
    for (int i = 0; i < MDNS.queryService("workstation", "tcp"); ++i) {
      if (MDNS.hostname(i).compareTo((String)HOST_NAME + (String)".local") == 0) serverIp = MDNS.IP(i);
    }
#endif
#ifdef ESP32
    serverIp = MDNS.queryHost(HOST_NAME);
#endif
  }
  Serial.print("resolved: ");
  Serial.println(serverIp.toString());
  
  //-----

  Udp.beginPacket(serverIp.toString().c_str(), 4101);
  Udp.write((const uint8_t *)"ok!", sizeof("ok!"));
  Udp.endPacket();
  digitalWrite(LED_BUILTIN, HIGH);
#ifdef ESP8266
  Serial.flush();
  Serial.swap();
#endif
}

void loop() {
#ifdef ESP8266
  MDNS.update(); // ESP8266 has to call MDNS.update();
  //if(Serial.available() > 0) {
    //Serial.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
#endif
//#ifdef ESP32
  if(Serial2.available() > 0) {
    Serial2.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
//#endif
    if(incomingTemp[0] == '+'){
      Udp.beginPacket(serverIp.toString().c_str(), 4101);
      Udp.write(incomingTemp, sizeof(incomingTemp));
      Udp.endPacket();
    }
  }
}

#ifdef ESP8266
#endif
#ifdef ESP32
#endif
