# POST /taobao/trade/memo/add
添加交易备注。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| tid | string | 是 | 交易订单 ID |
| memo | string | 是 | 备注内容 |
| flag | int | 否 | 旗帜标记 0~5，默认 0 |
