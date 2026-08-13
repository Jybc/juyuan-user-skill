# taobao_product_upshelf — 上架

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

将仓库中的商品上架到在售，可指定上架数量。

## 使用场景

- 将新发布的商品上架
- 重新上架之前下架的商品

## 前置条件

num_iid 通过 taobao_product_inventory 或 product_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `numIid` | `string` | 必填 | 商品数字 ID | `789012` |
| `num` | `int` | 可选 | 上架数量 | `1` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | `string` | 商品数字 ID |
| `result` | `object` | 上架结果 |

## 返回示例

```json
{"num_iid":"789012","result":{"status":"success"}}
```

## 关联 Tool

- **后续**: `taobao_product_list` — 确认已出现在在售列表中

## 降级

MCP 不可用时: `python scripts/driver.py taobao upshelf <shop_id> <num_iid> [num]`

## 常见错误

- 商品不存在或已上架
