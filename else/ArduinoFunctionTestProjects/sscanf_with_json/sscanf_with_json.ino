#include <ArduinoJson.h>
//char incomingTemp[] = "+UUDF:CCF9578E0D8A,-42,20,0,-43,37,\"CCF9578E0D89\",\"\",15869";
char incomingTemp[] = "+ok!!";
char instance_id[16];
char anchor_id[16];
int rssi, azimuth, elevation, reserved, channel;
unsigned int uudf_timestamp;

// Use https://arduinojson.org/v6/assistant to compute the capacity.
StaticJsonDocument<256> doc;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(incomingTemp);

  
  if(sscanf(incomingTemp, "+UUDF:%12s,%d,%d,%d,%d,%d,\"%12s\",\"\",%u",
            instance_id, &rssi, &azimuth, &elevation, &reserved, &channel, anchor_id, &uudf_timestamp))
  {
    doc["type"]        = "rssi+aoa";
    doc["data"]        = "measurement";
    doc["time"]        = 1351824120;
    doc["uudf_time"]   = uudf_timestamp;
    doc["instance_id"] = instance_id;
    doc["anchor_id"]   = anchor_id; 
    doc["rssi"]        = rssi;
    doc["azimuth"]     = azimuth;
    doc["elevation"]   = elevation;
    doc["channel"]     = channel;
    doc["message"]     = nullptr;
  }
  else
  {
    Serial.println("sscanf ERROR !!!");
    doc["type"]        = "rssi+aoa";
    doc["data"]        = "message";
    doc["time"]        = 1351824199;
    doc["uudf_time"]   = nullptr;
    doc["instance_id"] = nullptr;
    doc["anchor_id"]   = nullptr; 
    doc["rssi"]        = nullptr;
    doc["azimuth"]     = nullptr;
    doc["elevation"]   = nullptr;
    doc["channel"]     = nullptr;
    doc["message"]     = incomingTemp;
  }

  serializeJson(doc, Serial);
  Serial.println();
  serializeJsonPretty(doc, Serial);
}

void loop() {

}
