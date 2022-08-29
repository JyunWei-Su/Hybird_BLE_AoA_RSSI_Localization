/**
 * @version 1.3.0
 * @author  Jyun-wei, Su
 * @date    2022/08/29
 * @brief   brief description
 * @details 
 * @bug     none
 * @exception Unexpected "scan_evt timeout" on serial monitor
 *            @see https://github.com/espressif/arduino-esp32/issues/5860
 * @see Beacon scan exapmle: https://github.com/pcbreflux/espressif/blob/master/esp32/arduino/sketchbook/ESP32_BLE_beaconscan/ESP32_BLE_beaconscan.ino
 * @see BLEAdvertisedDevice usage: https://github.com/espressif/arduino-esp32/blob/master/libraries/BLE/src/BLEAdvertisedDevice.h
 * @Eddystone protocol specification: https://github.com/google/eddystone/blob/master/protocol-specification.md
 * 
  library: https://github.com/espressif/arduino-esp32/tree/master/libraries
 * @see scan duration https://esp32.com/viewtopic.php?t=2291
 * @note     @see https://github.com/espressif/arduino-esp32/pull/3995 
   Library had been update, so that need to add the second parameter: wantDuplicates
 * @see Calculate how much memory have to allocate to the JSON document using online tool: https://arduinojson.org/v6/assistant 
 * @note Make sure NTPClient_Generic.h only included in main .ino to avoid `Multiple Definitions` Linker Error
 *       @see https://github.com/khoih-prog/NTPClient_Generic
*/

#if defined(ESP32)
  #include <WiFi.h>
  #include <ESPmDNS.h>
  #include <BLEDevice.h>
  #include <BLEScan.h>
  #include <BLEAdvertisedDevice.h>
#else
  #error This code only support ESP32 boards.
#endif

#include <WiFiUdp.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESPNtpClient.h>

/***** DEDINE AND TYPEDEF *****/
//#define TIME_ZONE_OFFSET_HRS   (+8)
//#define NTP_UPDATE_INTERVAL_MS 60000L
#define DEVICE_TYPE   "rssi:esp32"
#define HOST_MDNS     "xplr-aoa.local"
#define WIFI_SSID     "XPLR-AOA"
#define WIFI_PASSWORD "12345678"
#define UDP_PORT       4102
#define MQTT_PORT      1883
//#define ENDIAN_CHANGE_U16(x) ((((x)&0xFF00)>>8) + (((x)&0xFF)<<8))

typedef enum JsonDocType
{
  DOC_INITIAL, DOC_MEASUREMENT, DOC_MESSAGE,
} JsonDocType;

/***** FUNCTION PROTOTYPE *****/
void setJsonDoc(JsonDocType docType);
void pubSubCallback(String topic, byte* message, unsigned int length);
void mqttSentStatus(const char *msg);

/***** GLOBAL VARIABLE *****/
String mDNS_name("ESP-");
// doc variable
char instance_id[16];
char anchor_id[16];
int wifi_rssi, rssi, channel;
unsigned long uudf_timestamp; // ms
unsigned long long unix_timestamp; // ms
int scanTime = 1; //In seconds
uint16_t EddystoneBeconUUID = 0xFEAA;
NTPEvent_t ntpEvent; // Last triggered event
int ntp_fail_count;

/***** OBJECT INSTANTIATION  *****/
WiFiUDP Udp;
WiFiClient espClient;
PubSubClient client(espClient);
IPAddress serverIp;
StaticJsonDocument<256> doc; // Have to calculate how much memory have to allocate
BLEScan* pBLEScan;

/***** DEFINE CUSTOM CLASS  *****/
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    std::string strServiceData = advertisedDevice.getServiceData();
    uint8_t cServiceData[128];
    strServiceData.copy((char *)cServiceData, strServiceData.length(), 0);

    if (advertisedDevice.getServiceDataUUID().equals(BLEUUID(EddystoneBeconUUID))==true) {  // found Eddystone UUID
      //-----
      //for (int i=0;i<strServiceData.length();i++) Serial.printf("[%02x]",cServiceData[i]); Serial.printf("\n");
      //unix_timestamp = timeClient.getUTCEpochMillis();
      unix_timestamp = (unsigned long long)NTP.millis();
      uudf_timestamp = millis();
      
      sprintf(instance_id, "%02X%02X%02X%02X%02X%02X", cServiceData[0x0C], cServiceData[0x0D], cServiceData[0x0E], cServiceData[0x0F], cServiceData[0x10], cServiceData[0x11]);
      rssi = advertisedDevice.getRSSI();
      Serial.printf("uudf time: %lu\tinstance_id: %s RSSI: %d\t\n",
                     millis(), instance_id, rssi);
      
      
      setJsonDoc(DOC_MEASUREMENT);
      Udp.beginPacket(serverIp.toString().c_str(), UDP_PORT);
      serializeJson(doc, Udp);
      Udp.endPacket();
    }
  }
};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);

  Serial.printf("\n");
  Serial.printf("=============================================\n");
  Serial.printf("               System Starting               \n"); 
  Serial.printf("=============================================\n");
  Serial.printf("Board Type        : %s\n", ARDUINO_BOARD);
  Serial.printf("Board MAC Address : %s\n", WiFi.macAddress().c_str());
  Serial.printf("=============================================\n");

  //=====Wifi AND mDNS CONFIG BEGIN=====
  mDNS_name += WiFi.macAddress();
  mDNS_name.replace(":", "");
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(mDNS_name.c_str()); // must be c sting
  //=====Wifi AND mDNS CONFIG END=====
  
  //=====Connect to Wifi BEGIN=====
  Serial.printf("Connecting To WiFi: %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.printf(".");
  }
  wifi_rssi = WiFi.RSSI();
  Serial.printf("connected: ");
  Serial.printf("%s, RSSI: %d\n", WiFi.localIP().toString().c_str(), wifi_rssi);
  //=====Connect to Wifi END=====

  //=====MQTT SETUP BEGIN=====
  Serial.printf("Setting MQTT      : ");
  client.setServer(HOST_MDNS, MQTT_PORT); // setup mqtt server and port
  client.setCallback(pubSubCallback); // setup mqtt broker callback function
  while(!client.connected()){
    delay(500);
    client.connect(mDNS_name.c_str());
    Serial.printf(".");
  }
  client.subscribe("anchor/restart");
  client.subscribe("anchor/online-check");
  Serial.printf("..Done.\n");
  //=====MQTT SETUP END
  
  //=====Startup mDNS Service BEGIN=====
  mqttSentStatus("Starting mDNS");
  Serial.printf("Starting mDNS     : %s", mDNS_name.c_str());
  if(!MDNS.begin(mDNS_name.c_str())) {
     Serial.printf("Error starting mDNS\n");
  }else{
    MDNS.addService("http", "tcp", 80);
    Serial.printf("started\n");
  }
  //=====Startup mDNS Service END=====
  
  //=====Resolving HOST IP BEGIN=====
  mqttSentStatus("Resolving HOST");
  Serial.printf("Resolving HOST    : %s ", HOST_MDNS);
  while(serverIp.toString() == IPAddress(INADDR_NONE).toString()) {
    delay(250);
    Serial.printf(".");
    int result = WiFi.hostByName(HOST_MDNS, serverIp);
  }
  Serial.printf("resolved: %s\n", serverIp.toString().c_str());
  //=====Resolving HOST IP END=====
  
  //=====Sync time to HOST BEGIN=====
  mqttSentStatus("Sync Time To HOST");
  ntp_fail_count = 0;
  unsigned long log_time = millis();
  NTP.setTimeZone(TZ_Asia_Taipei);
  NTP.onNTPSyncEvent([] (NTPEvent_t event) {ntpEvent = event;} ); // lambda function
  NTP.setNtpServerName(HOST_MDNS);
  NTP.setInterval(5,60); //Default: shortInterval=15s, longInterval=1800s; both need >=10
  NTP.begin();
  
  Serial.printf("Sync Time To HOST : %s", HOST_MDNS);
  while(ntpEvent.event != timeSyncd || NTP.getFirstSync() <= 0){
    if(millis() - log_time >= 3000) //delay(3000); // DO NOT USE DELAY WHEN SYNC TIME
    {
      log_time = millis();
      Serial.printf(".");
      ntp_fail_count ++;
      mqttSentStatus("Sync Time To HOST");
      if(ntp_fail_count >30){ ESP.restart(); }
    }
    delay(0);
  }
  Serial.printf("successed.\n");
  Serial.printf("UTC               : %llu\n", NTP.millis()); 
  Serial.printf("UNIX Timestamp(ms): %s\n" , NTP.getTimeDateStringUs ());
  //=====Sync time to HOST END=====

  Serial.printf("=============================================\n");
  // ^^^^^ Internet setup done. ^^^^^ //

  //=====Setup scaning device BEGIN=====
  Serial.println("Scanning...");
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); // create new scan
  pBLEScan->setInterval(100); // default is 100
  pBLEScan->setWindow(100);   // default is 100
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks(), true); // IMPORTANT: set the wantDuplicates to true
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  //=====Setup scaning device END=====
  // ^^^^^ BLE setup done. ^^^^^ //
  
  setJsonDoc(DOC_INITIAL); // Initial JSON document
  
  // Send ready packet to HOST
  Udp.beginPacket(serverIp.toString().c_str(), UDP_PORT);
  serializeJson(doc, Udp);
  Udp.endPacket();
  
  digitalWrite(LED_BUILTIN, HIGH);
  mqttSentStatus("Ready");
}

void loop() {
  if(WiFi.status() != WL_CONNECTED) ESP.restart();
  if(!client.loop()) client.connect(mDNS_name.c_str());
  //timeClient.update();
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
  pBLEScan->clearResults(); // Delete results fromBLEScan buffer to release memory
}

/***** FUNCTION DECLARATION *****/

/**
  * @brief JSON document setting function
  * @param size_t incomingSize; type JsonDocType
  */
void setJsonDoc(JsonDocType docType){
  if(docType == DOC_INITIAL)
  {
    doc["type"]        = DEVICE_TYPE;
    doc["data"]        = "message";
    //doc["unix_time"]   = timeClient.getUTCEpochMillis();
    doc["unix_time"]   = NTP.millis();
    doc["uudf_time"]   = millis();
    doc["instance_id"] = nullptr;
    String mac = String(WiFi.macAddress());
    mac.replace(":", "");
    doc["anchor_id"]   = mac;
    doc["rssi"]        = wifi_rssi;
    doc["channel"]     = nullptr;
    doc["message"]     = "Anchor Ready.";
  }
  else if(docType == DOC_MEASUREMENT)
  {
    doc["data"]        = "measurement";
    doc["unix_time"]   = unix_timestamp;
    doc["uudf_time"]   = uudf_timestamp;
    doc["instance_id"] = instance_id; 
    doc["rssi"]        = rssi;
    doc["channel"]     = channel;
    doc["message"]     = nullptr;
  }
  else if(docType == DOC_MESSAGE)
  {
    doc["data"]        = "message";
    doc["uudf_time"]   = nullptr;
    doc["anchor_id"]   = nullptr; 
    doc["rssi"]        = nullptr;
    doc["channel"]     = nullptr;
    doc["message"]     = nullptr;
  }
}


// 當設備發訊息給一個標題(topic)時，這段函式會被執行
void pubSubCallback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  // 假使收到訊息給主題 room/lamp, 可以檢查訊息是 on 或 off. 根據訊息開啟 GPIO
  if(topic == "anchor/restart"){
      Serial.print("Receive restart");
      mqttSentStatus("Restart");
      delay(500);
      ESP.restart();
  }
  else if (topic == "anchor/online-check"){
    mqttSentStatus("Online");
    //client.publish("anchor/online-check-response", mDNS_name.c_str());
  }
  
  Serial.println();
}

void mqttSentStatus(const char *msg){
  String topic("anchor/status/");
  topic += mDNS_name;
  client.publish(topic.c_str(), msg);
}
