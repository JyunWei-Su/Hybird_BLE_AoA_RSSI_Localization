# Tools
## Evaluation Software (GUI)
[s-center](https://www.u-blox.com/en/product/s-center)

## Anchor 燒錄
[u-connectLocate](https://www.u-blox.com/en/product/u-connectlocate?legacy=Current)

## Tag 燒錄
### [nrfutil](https://github.com/NordicSemiconductor/pc-nrfutil/releases)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/NordicSemiconductor/pc-nrfutil) [![License](https://img.shields.io/pypi/l/nrfutil.svg)](https://pypi.python.org/pypi/nrfutil)

### [c209_aoa_tag_for_dfu_boot](https://github.com/u-blox/c209-aoa-tag/releases)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/u-blox/c209-aoa-tag) ![GitHub](https://img.shields.io/github/license/u-blox/c209-aoa-tag)

## Tag 封包內容

* 可以使用[nRF Connect for Mobile](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp&hl=zh_TW&gl=US)掃描Tag取得詳細封包資訊
```json
{
  "beacon_type": "eddystone_uid",
  "distance": 3.7645762850240514,
  "eddystoneUidData": {
    "instance_id": "0x6c1deba41680",
    "namespace_id": "0x4e494e412d4234544147"
  },
  "hashcode": -1966824534,
  "isBlocked": false,
  "last_seen": 1662472557055,
  "manufacturer": 65194,
  "rssi": -47,
  "tx_power": -33
}
```
* 用ESP32 Arduino 範例掃描可以得到
`02 01 04 03 03 aa fe 17 16 aa fe 00 08 4e 49 4e 41 2d 42 34 54 41 47 6c 1d eb a4 16 80 00 00`
| LEN | TYPE | VALUE |
|:---:|:----:|-------|
|  02 | 0x01 | 0x04  |
|  03 | 0x03 | 0xAAFE|
|  23 | 0x16 | 0xAAFE084e494e412d42345441476c1deba416800000 |


