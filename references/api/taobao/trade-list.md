# GET /taobao/trade/list
订单列表。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| page | int | 否 | 页码，默认 1 |
| pagesize | int | 否 | 每页条数，默认 40，最大 100 |
| status | string | 否 | 状态筛选，如 WAIT_SELLER_SEND_GOODS |
