#include <NTPClient.h>
//#include "NTPClientExtension.h"
// change next line to use with another board/shield
#include <ESP8266WiFi.h>
//#include <WiFi.h> // for WiFi shield
//#include <WiFi101.h> // for WiFi 101 shield or MKR1000
#include <WiFiUdp.h>

const char *ssid     = "JWS_Mobile";
const char *password = "149597870700";
IPAddress ip(220,130,158,52);
//220.130.158.52
WiFiUDP ntpUDP;
NTPClient timeClient (ntpUDP, ip , 28800 , 1800000);
//time.stdtime.gov.tw
//clock.stdtime.gov.tw

void setup(){
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while ( WiFi.status() != WL_CONNECTED ) {
    delay ( 500 );
    Serial.print ( "." );
  }

  timeClient.begin();
}

void loop() {
  while(!timeClient.update()) {
    timeClient.forceUpdate();
    Serial.print("-");
  }

  Serial.println(timeClient.getFormattedTime());

  delay(1000);
}
