#include <ESPmDNS.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
  
const char* ssid     = "JWS_Mobile";
const char* password = "149597870700";
  
AsyncWebServer server(80);
  
void setup(){
  Serial.begin(115200);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
 
  if(!MDNS.begin("esp32")) {
     Serial.println("Error starting mDNS");
     return;
  }
  MDNS.addService("http", "tcp", 80); //https://techtutorialsx.com/2020/04/18/esp32-advertise-service-with-mdns/
  //MDNS.addServiceTxt("http", "tcp", "prop1", "test");
  //MDNS.addServiceTxt("http", "tcp", "prop2", "test2");
  
  Serial.println(WiFi.localIP());
  
  server.on("/hello", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/plain", "Hello World");
  });
  
  server.begin();
}
  
void loop(){}
