# taobao_rate_add — 追加评价

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

对已完成的订单追加评价（好评/中评/差评）。作为卖家给买家评价。

## 使用场景

- 订单完成后给买家评价
- 追加服务评价

## 前置条件

tid 通过 taobao_trade_list 获取（TRADE_FINISHED 状态）

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `tid` | `string` | 必填 | 淘宝订单号 | `t1001` |
| `result` | `string` | 必填 | good/neutral/bad | `good` |
| `content` | `string` | 可选 | 评价内容 | `感谢惠顾，欢迎再次光临` |
| `oid` | `string` | 可选 | 子订单号 | `o1001` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `tid` | `string` | 订单号 |
| `result` | `object` | 评价结果 |

## 返回示例

```json
{"tid":"t1001","result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao rate-add <shop_id> <tid> <result>`

## 常见错误

- 订单未完成不可评价
