/*
 * example from: https://github.com/pcbreflux/espressif/blob/master/esp32/arduino/sketchbook/ESP32_BLE_beaconscan/ESP32_BLE_beaconscan.ino
   BLEAdvertisedDevice usage: https://github.com/espressif/arduino-esp32/blob/master/libraries/BLE/src/BLEAdvertisedDevice.h
   Eddystone Protocol Specification: https://github.com/google/eddystone/blob/master/protocol-specification.md
   Ported to Arduino ESP32 by Evandro Copercini
*/

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include "BLEBeacon.h"
#include "BLEEddystoneTLM.h"
#include "BLEEddystoneURL.h"

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
      Serial.printf("\n");
      Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());
      Serial.printf("is Eddystone: %d %s length %d\n", advertisedDevice.getServiceDataUUID().bitSize(), advertisedDevice.getServiceDataUUID().toString().c_str(),strServiceData.length());
      Serial.printf("RSSI: %d, TxPWR: %d|%d, UUID: %s\n", advertisedDevice.getRSSI(), (int)advertisedDevice.getTXPower(), (int)advertisedDevice.haveTXPower(), advertisedDevice.getServiceUUID().toString().c_str());
      if (cServiceData[0]==0x00) { // UID
        BLEEddystoneURL oBeacon = BLEEddystoneURL();
        oBeacon.setData(strServiceData);
        Serial.printf("Eddystone Frame Type (Eddystone-URL) ");
        Serial.printf(oBeacon.getDecodedURL().c_str());
      } else if (cServiceData[0]==0x10) {
        BLEEddystoneURL oBeacon = BLEEddystoneURL();
        oBeacon.setData(strServiceData);
        Serial.printf("Eddystone Frame Type (Eddystone-URL) ");
        Serial.printf(oBeacon.getDecodedURL().c_str());
      } else if (cServiceData[0]==0x20) {
        BLEEddystoneTLM oBeacon = BLEEddystoneTLM();
        oBeacon.setData(strServiceData);
        Serial.printf("Eddystone Frame Type (Unencrypted Eddystone-TLM) \n");
        Serial.printf(oBeacon.toString().c_str());
      } else {
        for (int i=0;i<strServiceData.length();i++) {
        Serial.printf("[%X]",cServiceData[i]);
        }
      }
      Serial.printf("\n");
    }
  }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Scanning...");

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
}

void loop() {
  BLEScanResults foundDevices = pBLEScan->start(scanTime);
  Serial.printf("\nScan done! Devices found: %d\n",foundDevices.getCount());
  delay(5000);
}
