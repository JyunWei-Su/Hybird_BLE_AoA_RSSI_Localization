/*
 * BLEEddystoneTLM.cpp
 *
 *  Created on: Mar 12, 2018
 *      Author: pcbreflux
 */
#include "Arduino.h"
#include "sdkconfig.h"
#if defined(CONFIG_BT_ENABLED)
#include <string.h>
#include <esp_log.h>
#include "BLEEddystoneTLM.h"

static const char LOG_TAG[] = "BLEEddystoneTLM";
#define ENDIAN_CHANGE_U16(x) ((((x)&0xFF00)>>8) + (((x)&0xFF)<<8))
#define ENDIAN_CHANGE_U32(x) ((((x)&0xFF000000)>>24) + (((x)&0x00FF0000)>>8)) + ((((x)&0xFF00)<<8) + (((x)&0xFF)<<24))

BLEEddystoneTLM::BLEEddystoneTLM() {
  beconUUID = 0xFEAA;
  m_eddystoneData.frameType = EDDYSTONE_TLM_FRAME_TYPE;
  m_eddystoneData.version = 0;
  m_eddystoneData.volt = 3300; // 3300mV = 3.3V
  m_eddystoneData.temp = (uint16_t)((float)23.00);
  m_eddystoneData.advCount = 0;
  m_eddystoneData.tmil = 0;
} // BLEEddystoneTLM

std::string BLEEddystoneTLM::getData() {
	return std::string((char*)&m_eddystoneData, sizeof(m_eddystoneData));
} // getData

BLEUUID BLEEddystoneTLM::getUUID() {
	return BLEUUID(beconUUID);
} // getUUID

uint8_t BLEEddystoneTLM::getVersion() {
	return m_eddystoneData.version;
} // getVersion

uint16_t BLEEddystoneTLM::getVolt() {
	return m_eddystoneData.volt;
} // getVolt

float BLEEddystoneTLM::getTemp() {
	return (float)m_eddystoneData.temp;
} // getTemp

uint32_t BLEEddystoneTLM::getCount() {
	return m_eddystoneData.advCount;
} // getCount

uint32_t BLEEddystoneTLM::getTime() {
	return m_eddystoneData.tmil;
} // getTime

std::string BLEEddystoneTLM::toString() {
	std::string out = "";
  String buff;
  uint32_t rawsec;
  
  out += "Version ";
  buff = String(m_eddystoneData.version, DEC);
  out += buff.c_str();
  out += "\n";
  
  out += "Battery Voltage ";
  buff = String(ENDIAN_CHANGE_U16(m_eddystoneData.volt), DEC);
  out += buff.c_str();
  out += " mV\n";
  
  out += "Temperature ";
  buff = String((float)m_eddystoneData.temp, 1);
  out += buff.c_str();
  out += " °C\n";
  
  out += "Adv. Count ";
  buff = String(ENDIAN_CHANGE_U32(m_eddystoneData.advCount), DEC);
  out += buff.c_str();
  out += "\n";
  
  out += "Time ";
  rawsec = ENDIAN_CHANGE_U32(m_eddystoneData.tmil);
  buff = "0000"+String(rawsec/864000, DEC);
  out += buff.substring(buff.length()-4,buff.length()).c_str();
  out += ".";
  buff = "00"+String((rawsec/36000)%24, DEC);
  out += buff.substring(buff.length()-2,buff.length()).c_str();
  out += ":";
  buff = "00"+String((rawsec/600)%60, DEC);
  out += buff.substring(buff.length()-2,buff.length()).c_str();
  out += ":";
  buff = "00"+String((rawsec/10)%60, DEC);
  out += buff.substring(buff.length()-2,buff.length()).c_str();
  out += "\n";

	return out;
} // toString

/**
 * Set the raw data for the beacon record.
 */
void BLEEddystoneTLM::setData(std::string data) {
	if (data.length() != sizeof(m_eddystoneData)) {
		ESP_LOGE(LOG_TAG, "Unable to set the data ... length passed in was %d and expected %d", data.length(), sizeof(m_eddystoneData));
		return;
	}
  memcpy(&m_eddystoneData, data.data(), data.length());
} // setData

void BLEEddystoneTLM::setUUID(BLEUUID l_uuid) {
	beconUUID = l_uuid.getNative()->uuid.uuid16;
} // setUUID

void BLEEddystoneTLM::setVersion(uint8_t version) {
	m_eddystoneData.version = version;
} // setVersion

void BLEEddystoneTLM::setVolt(uint16_t volt) {
	m_eddystoneData.volt = volt;
} // setVolt

void BLEEddystoneTLM::setTemp(float temp) {
	m_eddystoneData.temp = (uint16_t)temp;
} // setTemp

void BLEEddystoneTLM::setCount(uint32_t advCount) {
	m_eddystoneData.advCount = advCount;
} // setCount

void BLEEddystoneTLM::setTime(uint32_t tmil) {
	m_eddystoneData.tmil = tmil;
} // setTime

#endif