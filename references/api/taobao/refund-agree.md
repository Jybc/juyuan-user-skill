# POST /taobao/refund/agree
同意退款（批量，子账号操作）。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| code | string | 是 | 验证码 |
| refund_infos | string | 是 | 退款信息 JSON 数组 |
| message | string | 否 | 操作说明 |
