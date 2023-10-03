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
 * @see NTPClient_Generic https://github.com/khoih-prog/NTPClient_Generic
 *                        To be included only in main(), .ino with setup() to avoid `Multiple Definitions` Linker Error
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
  
  #define Serial2 Serial
#elif defined(ESP32)
  #include <WiFi.h>
  #include <ESPmDNS.h>
#else
  #error This code only support ESP8266, ESP32 boards.
#endif

#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <NTPClient_Generic.h>

/***** DEDINE AND TYPEDEF *****/
#define TIME_ZONE_OFFSET_HRS            (+8)
#define NTP_UPDATE_INTERVAL_MS          60000L
#define HOST_NAME   "xplr-aoa"
#define WIFI_SSID  "XPLR-AOA"
#define WIFI_PASSWORD "12345678"
#define UDP_PORT 4101
#define DEVICE_TYPE "rssi+aoa:xplr-aoa"
typedef enum JsonDocType
{
  DOC_INITIAL,DOC_MEASUREMENT,DOC_MESSAGE,
} JsonDocType;

/***** FUNCTION PROTOTYPE *****/
void setJsonDoc(JsonDocType docType);
void debug_incomingTemp(void);

/***** GLOBAL VARIABLE *****/
//const char *ssid     = "XPLR-AOA";
//const char *password = "12345678";
char incomingTemp[128];
String mDNS_name("ESP-");
size_t incomingSize;
// doc variable
char instance_id[16];
char anchor_id[16];
int wifi_rssi, rssi, azimuth, elevation, reserved, channel;
unsigned int uudf_timestamp;

/*****  *****/
WiFiUDP Udp;
IPAddress serverIp;

// Use https://arduinojson.org/v6/assistant to compute the capacity.
//RAM Allocate to the json document
StaticJsonDocument<256> doc;
NTPClient timeClient(Udp, 3600*TIME_ZONE_OFFSET_HRS);


void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);

  // Reset XPLR-AoA Anchor START
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
  Serial2.print("\r"); // need to be \r
  //Serial2.flush();
  Serial2.print("AT+CPWROFF\r");
  //Serial2.flush();
#endif
  // Reset XPLR-AoA Anchor END

  Serial.println();
  Serial.println("=============================================");
  Serial.println("               System Starting               "); 
  Serial.println("=============================================");
  Serial.println("Board Type        : " + String(ARDUINO_BOARD));
  Serial.println("Board MAC Address : " + String(WiFi.macAddress()));
  Serial.println("=============================================");
  Serial.print("Connecting To WiFi: " + String(WIFI_SSID));

  // Wifi AND mDNS CONFIG START
  mDNS_name += WiFi.macAddress();
  mDNS_name.replace(":", "");
#ifdef ESP8266
  WiFi.hostname(mDNS_name.c_str());
#endif
#ifdef ESP32
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(mDNS_name.c_str()); // must be c sting
#endif
  // Wifi AND mDNS CONFIG END

  // Connect to Wifi START
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  wifi_rssi = WiFi.RSSI();
  Serial.print("connected: ");
  Serial.println(WiFi.localIP().toString() + ", RSSI: " + (String)wifi_rssi);
  // Connect to Wifi END
  
  // Startup mDNS Service START
  Serial.print("Starting mDNS     : " + mDNS_name);
  if(!MDNS.begin(mDNS_name.c_str())) {
     Serial.println("Error starting mDNS");
  }else{
    MDNS.addService("http", "tcp", 80);
    Serial.println(" ..started");
  }
  // Startup mDNS Service END
  
  // Resolving HOST IP START
  Serial.print("Resolving HOST    : " + String(HOST_NAME) + String(".local"));
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
  // Resolving HOST IP END
  
  // Sync time to HOST START
  timeClient.setPoolServerIP(serverIp);
  timeClient.setPoolServerName(NULL); // Because we use ip, must set server name to NULL
  timeClient.setUpdateInterval(NTP_UPDATE_INTERVAL_MS);
  timeClient.begin();

  Serial.print("Sync Time To HOST : " + timeClient.getPoolServerIP().toString());
  while(!timeClient.updated()){
    timeClient.update();
    delay(1000);
    Serial.print(".");
  }
  Serial.println("successed.");
  Serial.println("UTC               : " + timeClient.getFormattedTime()); 
  Serial.printf("UNIX Timestamp(ms): %llu\n" ,timeClient.getUTCEpochMillis());
  // Sync time to HOST START
  Serial.println("=============================================");
  
  // ^^^^^ Internet setup done. ^^^^^ //

  setJsonDoc(DOC_INITIAL); // Initial JSON document


  // Send Ready packet to HOST
  Udp.beginPacket(serverIp.toString().c_str(), UDP_PORT);
  serializeJson(doc, Udp);
  Udp.endPacket();
  
  digitalWrite(LED_BUILTIN, HIGH);
#ifdef ESP8266
  Serial.flush();
  Serial.swap();
#endif
}


void loop() 
{
  if(WiFi.status() != WL_CONNECTED) ESP.restart();
  timeClient.update();
#ifdef ESP8266
  // DO NOT SERIAL PRINT WHEN USING ESP8266
  MDNS.update(); // ESP8266 has to call MDNS.update();
  while(Serial.available() > 0) {
    incomingSize = Serial.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
#endif
#ifdef ESP32
  while(Serial2.available() > 0) {
    incomingSize = Serial2.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
#endif
    if(incomingSize <= sizeof(char) * 8) break; // invalid data
    doc["unix_time"] = timeClient.getUTCEpochMillis();
    int result = sscanf(incomingTemp, "+UUDF:%12s,%d,%d,%d,%d,%d,\"%12s\",\"\",%u",
                        instance_id, &rssi, &azimuth, &elevation, &reserved, &channel, anchor_id, &uudf_timestamp);
    if(result) setJsonDoc(DOC_MEASUREMENT);
    else       setJsonDoc(DOC_MESSAGE);
    
    Udp.beginPacket(serverIp.toString().c_str(), UDP_PORT);
    serializeJson(doc, Udp);
    Udp.endPacket();
  }
}


/***** FUNCTION DECLARATION *****/

/**
  * @brief JSON document setting function
  * @param document type JsonDocType
  */
void setJsonDoc(JsonDocType docType)
{
  if(docType == DOC_INITIAL)
  {
    doc["type"]        = "rssi+aoa";
    doc["data"]        = "message";
    doc["unix_time"]   = timeClient.getUTCEpochMillis();
    doc["uudf_time"]   = nullptr;
    doc["instance_id"] = nullptr;
    doc["anchor_id"]   = nullptr; 
    doc["rssi"]        = wifi_rssi;
    doc["azimuth"]     = nullptr;
    doc["elevation"]   = nullptr;
    doc["channel"]     = nullptr;
    doc["message"]     = "Anchor Ready.";
  }
  else if(docType == DOC_MEASUREMENT)
  {
    doc["data"]        = "measurement";
    doc["uudf_time"]   = uudf_timestamp;
    doc["instance_id"] = instance_id;
    doc["anchor_id"]   = anchor_id; 
    doc["rssi"]        = rssi;
    doc["azimuth"]     = azimuth;
    doc["elevation"]   = elevation;
    doc["channel"]     = channel;
    doc["message"]     = nullptr;
  }
  else if(docType == DOC_MESSAGE)
  {
    doc["data"]        = "message";
    doc["uudf_time"]   = nullptr;
    doc["instance_id"] = nullptr;
    doc["anchor_id"]   = nullptr; 
    doc["rssi"]        = nullptr;
    doc["azimuth"]     = nullptr;
    doc["elevation"]   = nullptr;
    doc["channel"]     = nullptr;
    doc["message"]     = incomingTemp;
  }
  else
  {
    doc["type"]        = "rssi+aoa";
    doc["data"]        = "error";
    doc["unix_time"]   = timeClient.getFormattedTime();
    doc["uudf_time"]   = nullptr;
    doc["instance_id"] = nullptr;
    doc["anchor_id"]   = nullptr; 
    doc["rssi"]        = nullptr;
    doc["azimuth"]     = nullptr;
    doc["elevation"]   = nullptr;
    doc["channel"]     = nullptr;
    doc["message"]     = "Unexpected Error.";
  }
}

/**
  * @brief Print out what Serial received
  */
void debug_incomingTemp()
{
#ifdef ESP8266
  Serial.flush();
  Serial.swap();
#endif
  Serial.println("========================DEBUG START============================");
  Serial.print("Len: ");
  Serial.println(strlen(incomingTemp));
  Serial.print("Size: ");
  Serial.println(incomingSize / sizeof(char));
  for(int i = 0; i < 16; i++){
    for(int j = 0; j < 8; j++){
      Serial.print((int)incomingTemp[8*i+j]);
      Serial.print('\t');
    }
    Serial.println();
  }
  Serial.println("========================DEBUG END============================\n");
#ifdef ESP8266
  Serial.flush();
  Serial.swap();
#endif
}
