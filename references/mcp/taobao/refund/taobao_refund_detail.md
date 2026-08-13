# taobao_refund_detail — 退款详情

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取退款单的完整详情：退款原因、金额、当前状态和退款版本号(refund_version)。退款版本号用于后续的同意/拒绝操作。

## 使用场景

- 同意/拒绝退款前查看详细原因
- 获取退款版本号用于后续操作

## 前置条件

refund_id 通过 taobao_refund_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `refundId` | `string` | 必填 | 退款单号 | `r1001` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `refund_id` | `string` | 退款单号 |
| `refund_version` | `string` | 退款版本号（同意/拒绝时需要） |
| `refund_fee` | `string` | 退款金额 |
| `reason` | `string` | 退款原因 |
| `status` | `string` | 退款状态 |

## 返回示例

```json
{"refund_id":"r1001","refund_version":"2","refund_fee":"88.00","reason":"尺码不合适","status":"WAIT_SELLER_AGREE"}
```

## 关联 Tool

- **后续**: `taobao_refund_agree / taobao_refund_refuse` — 根据退款原因和金额决定同意或拒绝

## 降级

MCP 不可用时: `python scripts/driver.py taobao refund-detail <shop_id> <refund_id>`

## 常见错误

- refund_id 不存在
