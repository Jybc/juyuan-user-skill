# taobao_refund_refuse — 拒绝退款

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

> ⚠️ 高风险操作 — 调用前需 `AskUserQuestion` 二次确认

## 简述

⚠️ 拒绝买家的退款申请。refund_version 必须与退款详情中的当前版本号一致（版本号不匹配会拒绝操作）。可能引发纠纷，调用前需二次确认。

## 使用场景

- 商品已发出买家申请仅退款
- 退款原因不合理需要拒绝

## 前置条件

refund_id 和 refund_version 通过 taobao_refund_detail 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `refundId` | `string` | 必填 | 退款单号 | `r1001` |
| `refundVersion` | `string` | 必填 | 退款版本号 | `2` |
| `refuseMessage` | `string` | 可选 | 拒绝原因说明 | `商品已发出，请先退货` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `refund_id` | `string` | 退款单号 |
| `result` | `object` | 拒绝结果 |

## 返回示例

```json
{"refund_id":"r1001","result":{"status":"success"}}
```

## 关联 Tool

- **前置**: `taobao_refund_detail` — 获取最新 refund_version

## 降级

MCP 不可用时: `python scripts/driver.py taobao refund-refuse <shop_id> <refund_id> <refund_version> [msg]`

## 常见错误

- 版本号不匹配（需重新获取 refund_detail）
- 退款状态已变更不允许拒绝
