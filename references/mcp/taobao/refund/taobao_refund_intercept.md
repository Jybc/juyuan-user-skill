# taobao_refund_intercept — 物流拦截

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

卖家主动发起物流拦截，阻止已发出的快递继续配送。通常用于买家申请退款但商品已在途的场景。

## 使用场景

- 已发货买家申请退款，拦截快递
- 发错货需要追回包裹

## 前置条件

refund_id 和 refund_version 通过 taobao_refund_detail 获取，订单已发货

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `refundId` | `string` | 必填 | 退款单号 | `r1001` |
| `refundVersion` | `string` | 必填 | 退款版本号 | `2` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `refund_id` | `string` | 退款单号 |
| `result` | `object` | 拦截结果 |

## 返回示例

```json
{"refund_id":"r1001","result":{"status":"success","message":"拦截请求已提交"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao refund-intercept <shop_id> <refund_id> <refund_version>`

## 常见错误

- 快递已签收无法拦截
- 物流公司不支持拦截
