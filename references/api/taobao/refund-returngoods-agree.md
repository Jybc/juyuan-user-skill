# POST /taobao/refund/returngoods-agree
同意退货。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| refund_id | string | 是 | 退款单 ID |
| refund_version | string | 是 | 退款版本号 |
| seller_address_id | string | 是 | 退货地址 ID |
| refund_phase | string | 否 | 退款阶段，默认 onsale |
