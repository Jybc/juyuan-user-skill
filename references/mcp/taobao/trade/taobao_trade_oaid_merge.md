# taobao_trade_oaid_merge — OAID 合并

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

将多个淘宝子订单合并为一个主子订单（OAID 合并），便于统一发货和管理。

## 使用场景

- 同一买家多件商品合并发货
- 合并拆分子订单

## 前置条件

订单号通过 taobao_trade_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `orderIds` | `array` | 必填 | 待合并的订单号列表 | `["t1001","t1002"]` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `order_ids` | `array` | 被合并的订单号 |
| `result` | `object` | 合并结果 |

## 返回示例

```json
{"order_ids":["t1001","t1002"],"result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao oaid-merge <shop_id> <order_ids...>`

## 常见错误

- 订单状态不允许合并
