/**
 * @version 1.1.0
 * @author  Jyun-wei, Su
 * @author  Ming-Yan, Tsai
 * @date    2022/07/07
 * @brief   brief description
 * @details 
 * @bug     ESP8266 mDNS advertise service actual work after entering loop()
 * @exception none
 * @see Calculate how much memory have to allocate to the JSON document using online tool: https://arduinojson.org/v6/assistant 
 * @see mDNS query servie on ESP32 Boards: https://techtutorialsx.com/2020/04/27/esp32-query-mdns-service/
 * @see mDNS advertise servie on ESP32 Boards: https://techtutorialsx.com/2020/04/18/esp32-advertise-service-with-mdns/
 * @see mDNS query servie on ESP8266 Boards: https://stackoverflow.com/questions/44187924/nodemcu-resolving-raspberrys-local-dns-through-mdns
 * @see mDNS advertise servie on ESP8266 Boards: https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266mDNS/examples/mDNS_Web_Server/mDNS_Web_Server.ino
 * @see Compile on both ESP32 and ESP8266: https://community.platformio.org/t/compile-on-both-esp32-and-esp8266/14356
 * @see How to send UDP packet: https://forum.arduino.cc/t/sending-udp-packets-from-an-esp8266-nodemcu/855730
 * @note Make sure NTPClient_Generic.h only included in main .ino to avoid `Multiple Definitions` Linker Error
 *       @see https://github.com/khoih-prog/NTPClient_Generic
 * @note When ESP8266 query mDNS service on Raspberrypi, you have to edit the following line in /etc/avahi/avahi-daemon.conf on Raspberrypi
 *       publish-workstation=no to publish-workstation=yes
 *       after than, sudo systemctl restart avahi-daemon.service to restart service
 *       @see https://raspberrypi.stackexchange.com/questions/117206/reaching-my-pi-with-mdns-avahi
 * @note You can add following lines to C:\Program Files (x86)\Arduino\lib\keywords.txt than your custom keywords will be highlighted
 *       # Custom Keywords (IMPORTANT: make sure using tab rather than white-space)
 *       DbgSerial KEYWORD1
 *       ComSerial KEYWORD1
 *       SerialSwitchTo KEYWORD1
 *       DBG_SERIAL  KEYWORD2
 *       COM_SERIAL  KEYWORD2
 * @note If yout want to find Board DEFINED, switch on File>Preferences>Compile Verbose in Arduino IDE.
 *       Then build/verify and inspect the output, you will see the -D defines that are passed to the compiler
 * @note The documenting of this file is following by Doxygen style
 */


#if defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <ESP8266mDNS.h>
#elif defined(ESP32)
  #include <WiFi.h>
  #include <ESPmDNS.h>
#else
  #error This code only support ESP8266, ESP32 boards.
#endif

#include <WiFiUdp.h>
#include <ArduinoJson.h>
//#include <NTPClient_Generic.h>
#include <ESPNtpClient.h>

/***** DEDINE SERIAL PORT *****/
#if defined(ARDUINO_ESP8266_GENERIC) // ESP01(ESP8266)
  #define ComSerial Serial  // Serial 0
  #define DbgSerial Serial  // Serial 2 by swap
  #define DEBUG_SERIAL_INIT_STATE false
#elif defined(ARDUINO_ESP8266_NODEMCU_ESP12E) // NodeMCU(ESP8266)
  #define ComSerial Serial  // Serial 2 by swap
  #define DbgSerial Serial  // Serial 0
  #define DEBUG_SERIAL_INIT_STATE true
#elif defined(ARDUINO_Node32s) // NodeMCU32s
  #define ComSerial Serial2 // Serial 2
  #define DbgSerial Serial  // Serial 0
  #define DEBUG_SERIAL_INIT_STATE true
#else
  #error Please define ComSerial and DbgSerial bt ARDUINO_BOARD
#endif

/***** DEDINE AND TYPEDEF *****/
//#define TIME_ZONE_OFFSET_HRS   (+8)
//#define NTP_UPDATE_INTERVAL_MS 60000L
#define DEVICE_TYPE   "rssi+aoa:xplr-aoa"
#define HOST_NAME     "xplr-aoa"
#define HOST_MDNS     "xplr-aoa.local"
#define WIFI_SSID     "XPLR-AOA"
#define WIFI_PASSWORD "12345678"
#define UDP_PORT       4101

typedef enum JsonDocType
{
  DOC_INITIAL, DOC_MEASUREMENT, DOC_MESSAGE,
} JsonDocType;

typedef enum SerialType
{
  DBG_SERIAL, COM_SERIAL,
} SerialType;

/***** FUNCTION PROTOTYPE *****/
void setJsonDoc(JsonDocType docType);
void SerialSwitchTo(SerialType serialType);
void debug_incomingTemp(void);

/***** GLOBAL VARIABLE *****/
char incomingTemp[128];
String mDNS_name("ESP-");
size_t incomingSize;
// doc variable
char instance_id[16];
char anchor_id[16];
int wifi_rssi, rssi, azimuth, elevation, reserved, channel;
unsigned long uudf_timestamp;
bool isDebugSerial;
NTPEvent_t ntpEvent; // Last triggered event
int ntp_fail_count;

/***** OBJECT INSTANTIATION  *****/
WiFiUDP Udp;
IPAddress serverIp;
StaticJsonDocument<256> doc; // Have to calculate how much memory have to allocate
//NTPClient timeClient(Udp, 3600*TIME_ZONE_OFFSET_HRS);

void setup()
{
  //pinMode(LED_BUILTIN, OUTPUT);
  //digitalWrite(LED_BUILTIN, LOW);
  isDebugSerial = DEBUG_SERIAL_INIT_STATE;
  if(!DbgSerial) DbgSerial.begin(115200);
  if(!ComSerial) ComSerial.begin(115200);
  
  //=====Reset XPLR-AoA Anchor BEGIN=====
  SerialSwitchTo(COM_SERIAL);
  ComSerial.printf("\r");
  ComSerial.printf("AT+CPWROFF\r");
  //=====Reset XPLR-AoA Anchor END=====

  SerialSwitchTo(DBG_SERIAL);
  DbgSerial.printf("\n");
  DbgSerial.printf("=============================================\n");
  DbgSerial.printf("               System Starting               \n"); 
  DbgSerial.printf("=============================================\n");
  DbgSerial.printf("Board Type        : %s\n", ARDUINO_BOARD);
  DbgSerial.printf("Board MAC Address : %s\n", WiFi.macAddress().c_str());
  DbgSerial.printf("Default Serial    : %s\n" , isDebugSerial ? "DEBUG": "COMMUNIATE");
  DbgSerial.printf("=============================================\n");
  DbgSerial.printf("Connecting To WiFi: %s", WIFI_SSID);

  //=====Wifi AND mDNS CONFIG BEGIN=====
  mDNS_name += WiFi.macAddress();
  mDNS_name.replace(":", "");
#ifdef ESP8266
  WiFi.hostname(mDNS_name.c_str());
#endif
#ifdef ESP32
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(mDNS_name.c_str()); // must be c sting
#endif
  //=====Wifi AND mDNS CONFIG END=====

  //=====Connect to Wifi BEGIN=====
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    DbgSerial.printf(".");
  }
  wifi_rssi = WiFi.RSSI();
  DbgSerial.printf("connected: ");
  DbgSerial.printf("%s, RSSI: %d\n", WiFi.localIP().toString().c_str(), wifi_rssi);
  //=====Connect to Wifi END=====
  
  //=====Startup mDNS Service BEGIN=====
  DbgSerial.printf("Starting mDNS     : %s", mDNS_name.c_str());
  if(!MDNS.begin(mDNS_name.c_str())) {
     DbgSerial.printf("Error starting mDNS\n");
  }else{
    MDNS.addService("http", "tcp", 80);
    DbgSerial.printf(" ..started\n");
  }
  //=====Startup mDNS Service END=====
  
  //=====Resolving HOST IP BEGIN=====
  DbgSerial.printf("Resolving HOST    : %s%s ", HOST_NAME, ".local");
  while ((serverIp.toString() == "(IP unset)") || (serverIp.toString() == "0.0.0.0")) {
    // (IP unset) is for esp8266, 0.0.0.0 is for esp32
    delay(250);
    DbgSerial.printf(".");
#ifdef ESP8266
    for (int i = 0; i < (int)MDNS.queryService("workstation", "tcp"); i++) {
      if (MDNS.hostname(i).compareTo((String)HOST_NAME + (String)".local") == 0) serverIp = MDNS.IP(i);
    }
#endif
#ifdef ESP32
    serverIp = MDNS.queryHost(HOST_NAME);
#endif
  }
  DbgSerial.printf("resolved: %s\n", serverIp.toString().c_str());
  //=====Resolving HOST IP END=====
  
  //=====Sync time to HOST BEGIN=====
  //timeClient.setPoolServerIP(serverIp);
  //timeClient.setPoolServerName(NULL); // Because we use IP mode, server name must set to NULL
  //timeClient.setUpdateInterval(NTP_UPDATE_INTERVAL_MS);
  //timeClient.begin();
  //DbgSerial.print("Sync Time To HOST : " + timeClient.getPoolServerIP().toString());
  //while(!timeClient.updated()){
  //  timeClient.update();
  //  delay(1000);
  //  DbgSerial.printf(".");
  //}
  //DbgSerial.printf("successed.\n");
  //DbgSerial.printf("UTC               : %s\n", timeClient.getFormattedTime().c_str()); 
  //DbgSerial.printf("UNIX Timestamp(ms): %llu\n" ,timeClient.getUTCEpochMillis());
  ntp_fail_count = 0;
  unsigned long log_time = millis();
  NTP.setTimeZone (TZ_Asia_Taipei);
  NTP.onNTPSyncEvent ([] (NTPEvent_t event) {ntpEvent = event; });
  NTP.setNtpServerName(HOST_MDNS);
  NTP.begin();
  
  DbgSerial.printf("Sync Time To HOST : %s", HOST_MDNS);
  while(ntpEvent.event != timeSyncd || NTP.getFirstSync() <= 0){
    if(millis() - log_time >= 3000) //delay(3000); // DO NOT USE DELAY WHEN SYNC TIME
    {
      log_time = millis();
      DbgSerial.printf(".");
      ntp_fail_count ++;
      if(ntp_fail_count >30){ESP.restart();}
    }
    delay(0);
  }
  DbgSerial.printf("successed.\n");
  DbgSerial.printf("UTC               : %llu\n", NTP.millis()); 
  DbgSerial.printf("UNIX Timestamp(ms): %s\n" , NTP.getTimeDateStringUs ());
  //=====Sync time to HOST END=====

  DbgSerial.printf("=============================================\n");
  // ^^^^^ Internet setup done. ^^^^^ //

  setJsonDoc(DOC_INITIAL); // Initial JSON document

  // Send ready packet to HOST
  Udp.beginPacket(serverIp.toString().c_str(), UDP_PORT);
  serializeJson(doc, Udp);
  Udp.endPacket();
  
  //digitalWrite(LED_BUILTIN, HIGH);
  SerialSwitchTo(COM_SERIAL);
}


void loop() 
{
  if(WiFi.status() != WL_CONNECTED) ESP.restart();
  //timeClient.update();
#ifdef ESP8266
  MDNS.update(); // ESP8266 need to call MDNS.update();
#endif
  while(ComSerial.available() > 0) {
    incomingSize = ComSerial.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
    if(incomingSize <= sizeof(char) * 8) break; // invalid data
    //doc["unix_time"] = timeClient.getUTCEpochMillis();
    doc["unix_time"] = NTP.millis();
    int result = sscanf(incomingTemp, "+UUDF:%12s,%d,%d,%d,%d,%d,\"%12s\",\"\",%lu",
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
    doc["type"]        = DEVICE_TYPE;
    doc["data"]        = "message";
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
}

/**
  * @brief Print out what Serial received
  */
void debug_incomingTemp()
{
  SerialSwitchTo(DBG_SERIAL);
  DbgSerial.println("========================DEBUG START============================");
  DbgSerial.print("Len: ");
  DbgSerial.println(strlen(incomingTemp));
  DbgSerial.print("Size: ");
  DbgSerial.println(incomingSize / sizeof(char));
  for(int i = 0; i < 16; i++){
    for(int j = 0; j < 8; j++){
      DbgSerial.print((int)incomingTemp[8*i+j]);
      DbgSerial.print('\t');
    }
    DbgSerial.println();
  }
  DbgSerial.println("========================DEBUG END============================\n");
  SerialSwitchTo(COM_SERIAL);
}

/**
  * @brief 
  */
void SerialSwitchTo(SerialType serialType)
{
  // Switch from ComSerial to DbgSerial
  if((!isDebugSerial) && serialType == DBG_SERIAL)
  {
    isDebugSerial = true;
#ifdef ESP8266
    Serial.flush();
    Serial.swap();
#endif
  }
  // Switch from DbgSerial to ComSerial
  else if((isDebugSerial) && serialType == COM_SERIAL)
  {
    isDebugSerial = false;
#ifdef ESP8266
    Serial.flush();
    Serial.swap();
#endif
  }
}
