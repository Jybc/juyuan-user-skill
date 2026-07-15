# POST /taobao/trade/update-address
修改收货地址。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| tid | string | 是 | 交易订单 ID |
| receiver_name | string | 否 | 收件人姓名 |
| receiver_mobile | string | 否 | 收件人手机 |
| receiver_state | string | 否 | 省份 |
| receiver_city | string | 否 | 城市 |
| receiver_district | string | 否 | 区县 |
| receiver_address | string | 否 | 详细地址 |
