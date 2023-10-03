/**
 * @version 1.3.0
 * @author  Jyun-wei, Su
 * @author  Ming-Yan, Tsai
 * @date    2022/08/29
 * @brief   brief description
 * @details 
 * @bug     ESP8266 mDNS advertise service actual work after entering loop()
 * @exception none
 * @see Calculate how much memory have to allocate to the JSON document using online tool: https://arduinojson.org/v6/assistant
 * @see mDNS advertise servie on both ESP8266 and ESP32 boards: https://www.arduino.cc/reference/en/libraries/wifinina/wifi.hostbyname/
 * @see mDNS query servie on ESP32 Boards: https://techtutorialsx.com/2020/04/27/esp32-query-mdns-service/
 * @see mDNS advertise servie on ESP32 Boards: https://techtutorialsx.com/2020/04/18/esp32-advertise-service-with-mdns/
 * @see mDNS query servie on ESP8266 Boards: https://stackoverflow.com/questions/44187924/nodemcu-resolving-raspberrys-local-dns-through-mdns
 * @see mDNS advertise servie on ESP8266 Boards: https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266mDNS/examples/mDNS_Web_Server/mDNS_Web_Server.ino
 * @see Compile on both ESP32 and ESP8266: https://community.platformio.org/t/compile-on-both-esp32-and-esp8266/14356
 * @see How to send UDP packet: https://forum.arduino.cc/t/sending-udp-packets-from-an-esp8266-nodemcu/855730
 * @note NTP liabrary use ESPNtpClient rather than NTPClient_Generic due to accuracy
 *       @see https://github.com/gmag11/ESPNtpClient/releases
 *       @version 0.2.7
 *       @code modify
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
 *       NTP KEYWORD1
 * @note If yout want to find Board DEFINED, switch on File>Preferences>Compile Verbose in Arduino IDE.
 *       Then build/verify and inspect the output, you will see the -D defines that are passed to the compiler
 * @note The documenting of this file is following by Doxygen style
 */

/*
https://github.com/khoih-prog/MySQL_MariaDB_Generic/releases
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

#include <MySQL_Generic.h>

#define MYSQL_DEBUG_PORT      Serial
#define _MYSQL_LOGLEVEL_      0  // Debug Level from 0 to 4

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
#define WIFI_SSID     "cadvlsi_lab610"
#define WIFI_PASSWORD "lab610250"

typedef enum SerialType
{
  DBG_SERIAL, COM_SERIAL,
} SerialType;

/***** FUNCTION PROTOTYPE *****/
void SerialSwitchTo(SerialType serialType);;

/***** GLOBAL VARIABLE *****/
size_t incomingSize;
char incomingTemp[128];

// doc variable
char instance_id[16];
char anchor_id[16];
int wifi_rssi, rssi, azimuth, elevation, reserved, channel;
unsigned long uudf_timestamp;
bool isDebugSerial;


char user[]         = "Lab610_DB";              // MySQL user login username
char password[]     = "lab610250";          // MySQL user login password
IPAddress server(140, 120, 90, 139);
uint16_t server_port = 3307;    //3306;
char default_database[] = "Lab610_DB";           //"test_arduino";
char default_table[]    = "Lab610_G_8";          //"test_arduino";

MySQL_Connection conn((Client *)&client);
MySQL_Query *query_mem;

String INSERT_SQL = String("INSERT INTO Lab610_DB.Lab610_G_8 (Receive_RSSI) VALUES( 12 )");
char sql_buffer[100];
/***** OBJECT INSTANTIATION  *****/
//WiFiUDP Udp;
//WiFiClient espClient;

void setup() {
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

  //=====Connect to Wifi BEGIN=====
  DbgSerial.printf("Connecting To WiFi: %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    DbgSerial.printf(".");
  }
  wifi_rssi = WiFi.RSSI();
  DbgSerial.printf("connected: ");
  DbgSerial.printf("%s, RSSI: %d\n", WiFi.localIP().toString().c_str(), wifi_rssi);
  //=====Connect to Wifi END=====

  // ^^^^^ Internet setup done. ^^^^^ //

  

  while(conn.connectNonBlocking(server, server_port, user, password) == RESULT_FAIL)
  {
    delay(500);
  }

  query_mem = new MySQL_Query(&conn);
  
  DbgSerial.printf("======mysql-ok============================================\n");
  SerialSwitchTo(COM_SERIAL);
}

void loop() {
  if(WiFi.status() != WL_CONNECTED) ESP.restart();

  while(ComSerial.available() > 0) {
    incomingSize = ComSerial.readBytesUntil('\n', incomingTemp, sizeof(incomingTemp) / sizeof(char) );
    if(incomingSize <= sizeof(char) * 8) break; // invalid data
    int result = sscanf(incomingTemp, "+UUDF:%12s,%d,%d,%d,%d,%d,\"%12s\",\"\",%lu",
                        instance_id, &rssi, &azimuth, &elevation, &reserved, &channel, anchor_id, &uudf_timestamp);

    //send here

    !query_mem->execute(sql_buffer);
    sprintf(sql_buffer, "INSERT INTO %s.%s (Receive_RSSI, Node_H, Node_T, Node_Heart) VALUES( %d, %d.0, %d.0, %d)", default_database, default_table, rssi, azimuth, elevation, channel);
  }
}

/***** FUNCTION DECLARATION *****/

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

