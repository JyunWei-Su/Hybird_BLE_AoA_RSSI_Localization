#include <Arduino.h>
// source code: https://github.com/gmag11/ESPNtpClient/tree/main/src
//#include "WifiConfig.h"

#include <ESPNtpClient.h>
#ifdef ESP32
#include <WiFi.h>
#else
#include <ESP8266WiFi.h>
#endif

#ifndef WIFI_CONFIG_H
#define YOUR_WIFI_SSID "XPLR-AOA"
#define YOUR_WIFI_PASSWD "12345678"
#endif // !WIFI_CONFIG_H

#define SHOW_TIME_PERIOD 1000
#define HOST_MDNS     "xplr-aoa.local"

const PROGMEM char* ntpServer = "xplr-aoa.local";
NTPEvent_t ntpEvent; // Last triggered event

void setup() {
    Serial.begin (115200);
    Serial.println ();
    Serial.println ("Connect to wifi...");
    WiFi.begin (YOUR_WIFI_SSID, YOUR_WIFI_PASSWD);
    while (WiFi.status() != WL_CONNECTED){
      delay(1000);
      Serial.printf(".");
    }

    Serial.println ("\nSync time to host...");
    NTP.setTimeZone (TZ_Asia_Taipei);
    NTP.setInterval (5,60); //Default: shortInterval=15s, longInterval=1800s; both need >=10
    Serial.printf("Interval      : %d\n", NTP.getInterval());
    Serial.printf("Short Interval: %d\n", NTP.getShortInterval());
    Serial.printf("Long Interval : %d\n", NTP.getLongInterval());
    NTP.onNTPSyncEvent ([] (NTPEvent_t event) {
        ntpEvent = event;
    });
    //NTP.setNtpServerName(HOST_MDNS);
    //NTP.begin ();
    NTP.begin (HOST_MDNS);
    
    unsigned long log_time = millis();
    while(ntpEvent.event != timeSyncd || NTP.getFirstSync() <= 0){
    if(millis() - log_time >= 3000) //delay(1000); // DO NOT USE DELAY WHEN SYNC TIME
    {
      log_time = millis();
      Serial.printf(".");
    }
    delay(0);
  }

    
}

void loop() {
    static int last = 0;

    if ((millis () - last) > SHOW_TIME_PERIOD) {
        last = millis ();
        Serial.print("Event:  ");
        Serial.println(ntpEvent.event);
        Serial.printf ("%d %s\n", ntpEvent.event, NTP.ntpEvent2str(ntpEvent));
        Serial.print("Interval:  ");
        Serial.println(NTP.getInterval());
        Serial.print("First:  ");
        Serial.println(NTP.getFirstSync());
        Serial.print("Last:   ");
        Serial.println(NTP.getLastNTPSync());
        Serial.print("Millis: ");
        Serial.println (millis());
        Serial.print("NTP_ms: ");
        Serial.println (NTP.millis());
        Serial.print("Time:   ");
        Serial.println (NTP.getTimeDateStringUs ());
        Serial.println();
    }
}
