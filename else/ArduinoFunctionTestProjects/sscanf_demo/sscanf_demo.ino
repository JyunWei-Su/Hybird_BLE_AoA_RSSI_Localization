
//char incomingTemp[] = "+UUDF:CCF9578E0D8A,-42,20,0,-43,37,\"CCF9578E0D89\",\"\",15869";
char incomingTemp[] = "+ok!!";
char instance_id[16];
char anchor_id[16];
int rssi, azimuth, elevation, reserved, channel;
unsigned int uudf_timestamp;

char *data = "28\"April\"2022";
int date = 0;
int year = 0;
char month[10];

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(incomingTemp);

  sscanf(data, "%d\"%5s\"%d", &date, month, &year);
  Serial.println(date);
  Serial.println(month);
  Serial.println(year);
  
  if(sscanf(incomingTemp, "+UUDF:%12s,%d,%d,%d,%d,%d,\"%12s\",\"\",%u",
            instance_id, &rssi, &azimuth, &elevation, &reserved, &channel, anchor_id, &uudf_timestamp))
  {
    Serial.println("OK !!!");
    Serial.println(instance_id);
    Serial.println(anchor_id);
    Serial.println(rssi);
    Serial.println(azimuth);
    Serial.println(elevation);
    Serial.println(reserved);
    Serial.println(channel);
  }
  else
  {
    Serial.println("sscanf ERROR !!!");
  }
}

void loop() {

}
