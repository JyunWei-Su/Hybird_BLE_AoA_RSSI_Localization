/****************************************************************************************************************************
  ESP_NTPClient_Advanced.ino

  For AVR, ESP8266/ESP32, SAMD21/SAMD51, nRF52, STM32, SAM DUE, WT32_ETH01, RTL8720DN boards using 
  a) Ethernet W5x00, ENC28J60, LAN8742A
  b) WiFiNINA
  c) ESP8266/ESP32 WiFi
  d) ESP8266/ESP32-AT-command WiFi
  e) WT32_ETH01 (ESP32 + LAN8720)
  f) RTL8720DN

  Based on and modified from Arduino NTPClient Library (https://github.com/arduino-libraries/NTPClient)
  to support other boards such as ESP8266/ESP32, SAMD21, SAMD51, Adafruit's nRF52 boards, SAM DUE, RTL8720DN, etc.
  and Ethernet/WiFi/WiFiNINA shields
  
  Copyright (C) 2015 by Fabrice Weinberg and licensed under MIT License (MIT)

  Built by Khoi Hoang https://github.com/khoih-prog/NTPClient_Generic
  Licensed under MIT license
 *****************************************************************************************************************************/

#if !( defined(ESP8266) ||  defined(ESP32) )
  #error This code is intended to run on the ESP8266 or ESP32 platform! Please check your Tools->Board setting.
#endif

#define NTP_DBG_PORT                Serial

// Debug Level from 0 to 4
#define _NTP_LOGLEVEL_              0

// To be included only in main(), .ino with setup() to avoid `Multiple Definitions` Linker Error
#include <NTPClient_Generic.h>          // https://github.com/khoih-prog/NTPClient_Generic

#if (ESP32)
  #include <WiFi.h>
#elif (ESP8266)
  #include <ESP8266WiFi.h>
#endif

#include <WiFiUdp.h>
#define HOST_NAME_WITH_DOMAIN "xplr-aoa.local"

const char *ssid     = "JWS_Mobile";
const char *pass = "149597870700";
IPAddress ntpIP(192,168,51,191);
WiFiUDP ntpUDP;

// NTP server
//World
char timeServer[] = "pool.ntp.org";
//char timeServer[] = "time.nist.gov";
// Canada
//char timeServer[] = "0.ca.pool.ntp.org";
//char timeServer[] = "1.ca.pool.ntp.org";
//char timeServer[] = "2.ca.pool.ntp.org";
//char timeServer[] = "3.ca.pool.ntp.org";
// Europe
//char timeServer[] = ""europe.pool.ntp.org";

#define TIME_ZONE_OFFSET_HRS            (+8)
#define NTP_UPDATE_INTERVAL_MS          60000L
#define HOST_NAME   "xplr-aoa"
// You can specify the time server pool and the offset (in seconds, can be
// changed later with setTimeOffset() ). Additionaly you can specify the
// update interval (in milliseconds, can be changed using setUpdateInterval() ).
//NTPClient timeClient(ntpUDP, timeServer, (3600 * TIME_ZONE_OFFSET_HRS), NTP_UPDATE_INTERVAL_MS);
//NTPClient timeClient(ntpUDP, ntpIP, (3600 * TIME_ZONE_OFFSET_HRS), NTP_UPDATE_INTERVAL_MS);
NTPClient timeClient(ntpUDP,3600 * TIME_ZONE_OFFSET_HRS);


void setup()
{
  Serial.begin(115200);
  while (!Serial && millis() < 5000);

  Serial.println("\nStarting ESP_NTPClient_Advanced on " + String(ARDUINO_BOARD));
  Serial.println(NTPCLIENT_GENERIC_VERSION);

  Serial.println("Connecting to: " + String(ssid));

  WiFi.begin(ssid, pass);

  while ( WiFi.status() != WL_CONNECTED )
  {
    delay ( 500 );
    Serial.print ( "." );
  }

  Serial.print(F("\nESP_NTPClient_Advanced started @ IP address: "));
  Serial.println(WiFi.localIP());
  timeClient.setPoolServerIP(ntpIP);
  timeClient.setPoolServerName(HOST_NAME_WITH_DOMAIN);
  timeClient.setUpdateInterval(NTP_UPDATE_INTERVAL_MS);
  timeClient.begin();

  Serial.print("Using NTP Server: " + timeClient.getPoolServerName() + " ");
  Serial.println(timeClient.getPoolServerIP());
  
  
}

void loop()
{
  timeClient.update();


  if (timeClient.updated())
    Serial.println("********UPDATED********");
  else
    Serial.println("******NOT UPDATED******");

  Serial.println("UTC : " + timeClient.getFormattedTime()); 
  Serial.print("UNIX Timestamp(ms): ");
  Serial.println(timeClient.getUTCEpochMillis());

  delay(1000);
}
