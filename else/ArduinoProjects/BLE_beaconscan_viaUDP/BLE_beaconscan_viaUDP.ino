/*
 * example from: https://github.com/pcbreflux/espressif/blob/master/esp32/arduino/sketchbook/ESP32_BLE_beaconscan/ESP32_BLE_beaconscan.ino
   BLEAdvertisedDevice usage: https://github.com/espressif/arduino-esp32/blob/master/libraries/BLE/src/BLEAdvertisedDevice.h
   Eddystone Protocol Specification: https://github.com/google/eddystone/blob/master/protocol-specification.md
   Ported to Arduino ESP32 by Evandro Copercini
*/

#if defined(ESP32)
#include <WiFi.h>
#include <ESPmDNS.h>
#include <BLEDevice.h>
//#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
//#include "BLEBeacon.h"
#define CLIENT_NAME "nodemcu32s"
#else
#error This code only support ESP32 boards.
#endif

#define HOST_NAME   "xplr-aoa"
const char* ssid     = "XPLR-AOA";
const char* password = "12345678";
static unsigned char incomingTemp[100];
WiFiUDP Udp;
IPAddress serverIp;

BLEScan* pBLEScan;
int scanTime = 5; //In seconds
uint16_t beconUUID = 0xFEAA;
#define ENDIAN_CHANGE_U16(x) ((((x)&0xFF00)>>8) + (((x)&0xFF)<<8))

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    std::string strServiceData = advertisedDevice.getServiceData();
    uint8_t cServiceData[100];
    strServiceData.copy((char *)cServiceData, strServiceData.length(), 0);

    if (advertisedDevice.getServiceDataUUID().equals(BLEUUID(beconUUID))==true) {  // found Eddystone UUID
      //Serial.printf("\n");
      //Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());
      //Serial.printf("is Eddystone: %d %s length %d\n", advertisedDevice.getServiceDataUUID().bitSize(), advertisedDevice.getServiceDataUUID().toString().c_str(),strServiceData.length());
      Serial.printf("RSSI: %d, TxPWR: %d|%d, UUID: %s\n", advertisedDevice.getRSSI(), (int)advertisedDevice.getTXPower(), (int)advertisedDevice.haveTXPower(), advertisedDevice.getServiceUUID().toString().c_str());
      //-----
      String rssi = (String)(advertisedDevice.getRSSI());
      Udp.beginPacket(serverIp.toString().c_str(), 4102);
      Udp.write((const uint8_t*)rssi.c_str(), sizeof(rssi.c_str()));
      Udp.endPacket();
      //-----
      if (cServiceData[0]==0x00) { // UID
        for (int i=0;i<strServiceData.length();i++) {
        //Serial.printf("[%X]",cServiceData[i]);
        }
      } else {
        for (int i=0;i<strServiceData.length();i++) {
        //Serial.printf("[%X]",cServiceData[i]);
        }
      }
      //Serial.printf("\n");
    }
  }
};

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);

  Serial.println();
  Serial.print("Connecting to WiFi..");
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(CLIENT_NAME);
  WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.print("connected: ");
  Serial.println(WiFi.localIP().toString() + " RSSI:" + (String)WiFi.RSSI());
  
  // -----mDNS
  Serial.print("Starting MDNS..");
  if(!MDNS.begin(CLIENT_NAME)) {
     Serial.println("Error starting mDNS");
  }else{
    MDNS.addService("http", "tcp", 80);
    Serial.println("started");
  }
  Serial.print("Resolving host..");
  while ((serverIp.toString() == "(IP unset)") || (serverIp.toString() == "0.0.0.0")) {
    // (IP unset) is for esp8266, 0.0.0.0 is for esp32
    delay(250);
    Serial.print(".");
    serverIp = MDNS.queryHost(HOST_NAME);
  }
  Serial.print("resolved: ");
  Serial.println(serverIp.toString());
  
  //-----

  Udp.beginPacket(serverIp.toString().c_str(), 4101);
  Udp.write((const uint8_t *)"ok!", sizeof("ok!"));
  Udp.endPacket();
  digitalWrite(LED_BUILTIN, HIGH);

  //-----
  Serial.println("Scanning...");

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
}

void loop() {
  BLEScanResults foundDevices = pBLEScan->start(scanTime);
  //Serial.printf("\nScan done! Devices found: %d\n",foundDevices.getCount());
  
}
