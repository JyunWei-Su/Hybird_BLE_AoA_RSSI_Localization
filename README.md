# Hybird_BLE_AoA_RSSI_Localization

 Hybird_BLE_AoA_RSSI_Localization AoA專題 
 123

### User Name And Password
For the convenience of the experiment, all users and passwords are as follows.
#### Wifi AP
SSID: `xplr-aoa`
PASSWORD : `12345678`
#### Raspberry Pi
HOST NAME: `xplr-aoa`
USER NAME: `xplr-aoa`
PASSWORD : `12345678`
#### PostgreSQL
USER NAME: `xplr-aoa`
PASSWORD : `12345678`
#### Test
test

## note
used the option Run -> Add Configuration (or Open configuration, if available) This will open your current 'launch.json' file. Now you may add this line to the configuration wanted (in my case was Python):

`"cwd": "${fileDirname}"`

## 重要 anchor編譯後需要檢查是否有同步
將Tag設為1Hz
開UDP server 監聽封包檢查是否同步