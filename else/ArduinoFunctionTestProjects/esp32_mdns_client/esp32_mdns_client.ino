#include <WiFi.h>
#include <ESPmDNS.h>
 
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
   
void setup() {
   
  Serial.begin(115200);
   
  WiFi.begin(ssid, password);
     
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
     
  while(mdns_init()!= ESP_OK){
    delay(1000);
    Serial.println("Starting MDNS...");
  }
 
  Serial.println("MDNS started");
 
  IPAddress serverIp;
 
  while (serverIp.toString() == "0.0.0.0") {
    Serial.println("Resolving host...");
    delay(250);
    serverIp = MDNS.queryHost("raspberrypi-test");
  }
 
  Serial.println("Host address resolved:");
  Serial.println(serverIp.toString());   
 
}
   
void loop() {}
