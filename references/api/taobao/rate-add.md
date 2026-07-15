# POST /taobao/rate/add
新增评价。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| tid | string | 是 | 交易订单 ID |
| result | string | 是 | good/neutral/bad |
| content | string | 否 | 评价内容 |
| oid | string | 否 | 子订单 ID |
| anony | bool | 否 | 是否匿名 |
