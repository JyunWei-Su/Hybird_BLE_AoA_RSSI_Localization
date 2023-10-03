/*
 * DS3231DateTime.cpp
 *
 * Copyright 2017 Christopher B. Liebman
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 *
 *  Created on: May 22, 2017
 *      Author: chris.l
 */

#include "DS3231DateTime.h"

static PROGMEM const char TAG[] = "DS3231DateTime";

#define dbvalue(prefix) { \
    dlog.debug(FPSTR(TAG), F("%s position:%u (%04u-%02u-%02u %02u:%02u:%02u) weekday:%u century:%d unix:%lu"), \
            prefix, \
            getPosition(), \
            year+1900+100, \
            month, \
            date, \
            hours, \
            minutes, \
            seconds, \
            day, \
            century, \
            getUnixTime());}


DS3231DateTime::DS3231DateTime()
{
    seconds = 0;
    minutes = 0;
    hours = 0;
    date = 0;
    day = 0;
    month = 0;
    year = 0;
    century = 0;
}

boolean DS3231DateTime::isValid()
{
    dbvalue("DS3231DateTime::isValid");

    if (seconds > 59)
    {
        dlog.error(FPSTR(TAG), F("::isValid: invalid seconds %d"), seconds);
        return false;
    }

    if (minutes > 59)
    {
        dlog.error(FPSTR(TAG), F("::isValid: invalid minutes %d"), minutes);
        return false;
    }

    if (hours > 23)
    {
        dlog.error(FPSTR(TAG), F("::isValid: invalid hours %d"), hours);
        return false;
    }

    if (date > 31)
    {
        dlog.error(FPSTR(TAG), F("::isValid: invalid hours %d"), hours);
        return false;
    }

    if ((month > 12) || (month < 1))
    {
        dlog.error(FPSTR(TAG), F("::isValid: invalid month %d"), month);
        return false;
    }

    if (year > 99)
    {
        dlog.error(FPSTR(TAG), F("::isValid: invalid year %d"), year);
        return false;
    }

    return true;
}

void DS3231DateTime::setUnixTime(unsigned long time)
{
    struct tm tm;
    TimeUtils::gmtime_r((time_t*)&time, &tm);

    dlog.debug(FPSTR(TAG), F("::setUnixTime month: %d"), tm.tm_mon);

    seconds = tm.tm_sec;
    minutes = tm.tm_min;
    hours   = tm.tm_hour;
    day     = tm.tm_wday;
    date    = tm.tm_mday;
    month   = tm.tm_mon  + 1;
    year    = tm.tm_year - 100;
    century = 0;
    dbvalue("setUnixTime new value:");
}

unsigned long DS3231DateTime::getUnixTime()
{
    struct tm tm;
    tm.tm_sec   = seconds;
    tm.tm_min   = minutes;
    tm.tm_hour  = hours;
    tm.tm_mday  = date;
    tm.tm_mon   = month - 1;
    tm.tm_year  = year  + 100;
    tm.tm_isdst = 0;
    tm.tm_wday  = 0;
    tm.tm_yday  = 0;
    unsigned long unix = TimeUtils::mktime(&tm);
    dlog.debug(FPSTR(TAG), F("::getUnixTime: returning unix time: %lu"), unix);
    return unix;
}

void DS3231DateTime::applyOffset(int offset)
{
    unsigned long now = getUnixTime();
    now += offset;
    setUnixTime(now);
}

uint16_t DS3231DateTime::getPosition()
{
    int h = hours;
    if (h > 12)
    {
        h -= 12;
    }
    return h*3600 + minutes*60 + seconds;
}

uint16_t DS3231DateTime::getPosition(int offset)
{
    int signed_position = getPosition();
    dlog.debug(FPSTR(TAG), F("::getPosition: position before offset: %d"), signed_position);
    signed_position += offset;
    dlog.debug(FPSTR(TAG), F("::getPosition: position after offset: %d"), signed_position);
    if (signed_position < 0)
    {
        signed_position += MAX_POSITION;
        dlog.debug(FPSTR(TAG), F("::getPosition: position corrected+: %d"), signed_position);
    }
    else if (signed_position >= MAX_POSITION)
    {
        signed_position -= MAX_POSITION;
        dlog.debug(FPSTR(TAG), F("::getPosition: position corrected-: %d"), signed_position);
    }
    uint16_t position = (uint16_t) signed_position;
    return position;
}

char value_buf[128];

const char* DS3231DateTime::string()
{
    snprintf(value_buf, 127,
            "%04u-%02u-%02u %02u:%02u:%02u",
            year+1900+100,
            month,
            date,
            hours,
            minutes,
            seconds);
    return value_buf;
}

uint8_t DS3231DateTime::getDay()
{
    return day;
}

uint8_t DS3231DateTime::getDate()
{
    return date;
}

uint8_t DS3231DateTime::getHour()
{
    return hours;
}

uint8_t DS3231DateTime::getMonth()
{
    return month;
}

uint16_t DS3231DateTime::getYear()
{
    return year+2000;
}

