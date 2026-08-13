# taobao_refund_agree — 同意退款

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

> ⚠️ 高风险操作 — 调用前需 `AskUserQuestion` 二次确认

## 简述

⚠️ 同意买家的退款申请，资金将从店铺账户扣除。操作不可逆。调用前需二次确认。

## 使用场景

- 买家申请退款且理由合理
- 售后协商一致同意退款

## 前置条件

refund_json 通过 taobao_refund_detail 获取完整退款数据

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `code` | `string` | 必填 | 验证码或退款编码 | `ok` |
| `refundJson` | `string` | 必填 | 退款 JSON 数据（从 refund_detail 获取） | `{"refund_id":"r1001","refund_fee":"88.00",...}` |
| `message` | `string` | 可选 | 同意说明 | `已同意退款，金额将原路返回` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `result` | `object` | 退款结果 |

## 返回示例

```json
{"result":{"status":"success","message":"退款已处理"}}
```

## 关联 Tool

- **前置**: `taobao_refund_detail` — 获取完整退款 JSON 数据

## 降级

MCP 不可用时: `python scripts/driver.py taobao refund-agree <shop_id> <code> <refund_json>`

## 常见错误

- 余额不足
- 退款状态已变更
