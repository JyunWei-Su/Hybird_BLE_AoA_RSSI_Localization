#include <ArduinoJson.h>
StaticJsonDocument<256> doc;
void setup() {
  Serial.begin(115200);
  while (!Serial) continue;
  Serial.println();

  // Allocate the JSON document
  //
  // Inside the brackets, 200 is the RAM allocated to this document.
  // Don't forget to change this value to match your requirement.
  // Use https://arduinojson.org/v6/assistant to compute the capacity.

  // StaticJsonObject allocates memory on the stack, it can be
  // replaced by DynamicJsonDocument which allocates in the heap.
  //
  // DynamicJsonDocument  doc(200);

  
  
  doc["type"] = "rssi+aoa";
  doc["data"] = "measurement";
  doc["time"] = 1351824120;
  doc["instance_id"] = "CCF9578E0D8A";
  doc["rssi"] = -42;
  doc["azimuth"] = 90;
  doc["elevation"] = -90;
  doc["channel"] = 37;
  doc["anchor_id"] = "CCF9578E0D89";
  

  serializeJson(doc, Serial);

  Serial.println();


  serializeJsonPretty(doc, Serial);
}

void loop() {
  // not used in this example
}
