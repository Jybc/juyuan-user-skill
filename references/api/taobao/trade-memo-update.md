# POST /taobao/trade/memo/update
更新交易备注。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| tid | string | 是 | 交易订单 ID |
| memo | string | 是 | 新备注内容 |
| flag | int | 否 | 旗帜标记 0~5 |
| reset | bool | 否 | 是否重置旗子 |
