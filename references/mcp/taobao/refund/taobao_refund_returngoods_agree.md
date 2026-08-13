# taobao_refund_returngoods_agree — 同意退货

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

同意买家的退货申请，提供卖家退货地址。买家退货后需确认收货再退款。

## 使用场景

- 买家申请退货退款
- 需要买家先退货再退款

## 前置条件

refund_id 和 refund_version 通过 taobao_refund_detail 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `refundId` | `string` | 必填 | 退款单号 | `r1001` |
| `refundVersion` | `string` | 必填 | 退款版本号 | `2` |
| `sellerAddressId` | `string` | 必填 | 退货地址 ID | `1` |
| `refundPhase` | `string` | 可选 | 退款阶段 | `` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `refund_id` | `string` | 退款单号 |
| `result` | `object` | 同意退货结果 |

## 返回示例

```json
{"refund_id":"r1001","result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao returngoods-agree <shop_id> <refund_id> <refund_version> <address_id>`

## 常见错误

- 版本号不匹配
