# taobao_product_delete — 删除商品

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

> ⚠️ 高风险操作 — 调用前需 `AskUserQuestion` 二次确认

## 简述

⚠️ 永久删除淘宝商品，不可恢复。调用前需二次确认。

## 使用场景

- 彻底移除不再销售的商品
- 清退违规商品

## 前置条件

num_iid 通过 taobao_product_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `numIid` | `string` | 必填 | 商品数字 ID | `789012` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | `string` | 被删除的商品 ID |
| `result` | `object` | 删除结果 |

## 返回示例

```json
{"num_iid":"789012","result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao delete <shop_id> <num_iid>`

## 常见错误

- 商品不存在或已删除
