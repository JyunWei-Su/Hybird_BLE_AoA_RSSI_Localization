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

## Arduino NTP Liberary
* 使用 gmag11 的 [ESPNtpClient]https://github.com/gmag11/ESPNtpClient/releases
* Version: 0.2.7
### 手動修改 Library
* 由於 Library 本身的限制及缺陷，會倒致連線NTP需要較久時間，因此需要以下手動更改
* 修改後將提升 NTP 對時失敗時重新連線的 Interval
* 檔案資料夾：C:\Users\User\Documents\Arduino\libraries\ESPNtpClient-0.2.7\src
* ESPNtpClient.h
    * 將 line 43 `constexpr auto DEFAULT_NTP_TIMEOUT` 從 `5000` 改為 `2000`
    * 將 line 46 `MIN_NTP_INTERVAL` 從 `10` 改為 `5`
* ESPNtpClient.h
    * 將 line 628 `if (ntpServerIPAddress == IPAddress(INADDR_NONE))` 改為 `if (ntpServerIPAddress.toString() == IPAddress(INADDR_NONE).toString())` (issue [#43](https://github.com/gmag11/ESPNtpClient/issues/43))
    * 將 line 607 下新增一行 `actualInterval = ntpTimeout + 500;`