#include <NTPClient.h>
// change next line to use with another board/shield
#include <ESP8266WiFi.h>
//#include <WiFi.h> // for WiFi shield
#include <WiFiUdp.h>

IPAddress ip(192,168,51,30);
IPAddress gateway(192,168,51,51);
IPAddress subnet(255,255,255,0);
IPAddress dns(192,168,51,51);   

const char *ssid     = "JWS_Mobile";
const char *password = "149597870700";

WiFiUDP ntpUDP;

// You can specify the time server pool and the offset (in seconds, can be
// changed later with setTimeOffset() ). Additionaly you can specify the
// update interval (in milliseconds, can be changed using setUpdateInterval() ).
NTPClient timeClient(ntpUDP, "time.stdtime.gov.tw", 28800, 60000);

void setup(){
  Serial.begin(115200);
  WiFi.config(ip, gateway, subnet, dns);
  WiFi.begin(ssid, password);

  while ( WiFi.status() != WL_CONNECTED ) {
    delay ( 500 );
    Serial.print ( "." );
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  timeClient.begin();
  timeClient.setTimeOffset(28800); // GMT +8 = 28800
}

void loop() {
  while(!timeClient.update()) {
    timeClient.forceUpdate();
    Serial.print(".");
  }

  Serial.println(timeClient.getFormattedTime());

  delay(1000);
}
