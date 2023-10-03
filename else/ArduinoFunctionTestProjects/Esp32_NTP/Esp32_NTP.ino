/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com
  Based on the NTP Client library example
*********/

#include <WiFi.h>
#include <NTPClient.h> // https://github.com/taranais/NTPClient/archive/master.zip
#include <WiFiUdp.h>
#include <ESPmDNS.h>

IPAddress ip(192,168,51,30);
IPAddress dns(192,168,51,51); 
IPAddress gateway(192,168,51,51);   
IPAddress subnet(255,255,255,0);

// Replace with your network credentials
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
String hostname= "ESP32 Node";

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "time.stdtime.gov.tw", 28800, 60000);

// Variables to save date and time
String formattedDate;
String dayStamp;
String timeStamp;

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  // -----
  // https://stackoverflow.com/questions/54907985/esp32-fails-on-set-wifi-hostname
  WiFi.disconnect();
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE);  // This is a MUST!
  WiFi.setHostname("myFancyESP32");
  Serial.print("Host name:");
  Serial.println(WiFi.getHostname());
  // -----
  //WiFi.setHostname(hostname.c_str()); //https://microcontrollerslab.com/set-esp32-custom-hostname-arduino-ide/
  //WiFi.config(ip, gateway, subnet, dns);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // -----
  // 
  while(!MDNS.begin("myFancyESP32")) {
     Serial.println("Starting mDNS...");
     delay(1000);
  }
  Serial.println("MDNS started"); 

// Initialize a NTPClient to get time
  timeClient.begin();
  Serial.println("timeClient had begined");
  //timeClient.setTimeOffset(28800); // GMT +8 = 28800
}
void loop() {
  while(!timeClient.update()) {
    timeClient.forceUpdate();
    Serial.print(".");
  }
  // The formattedDate comes with the following format:
  // 2018-05-28T16:00:13Z
  // We need to extract date and time
  formattedDate = timeClient.getFormattedDate();
  Serial.println(formattedDate);
  Serial.println(millis());

  // Extract date
  /*int splitT = formattedDate.indexOf("T");
  dayStamp = formattedDate.substring(0, splitT);
  Serial.print("DATE: ");
  Serial.println(dayStamp);
  // Extract time
  timeStamp = formattedDate.substring(splitT+1, formattedDate.length()-1);
  Serial.print("HOUR: ");
  Serial.println(timeStamp);*/
  delay(1000);
}
