# taobao_product_inventory — 库存查询

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝店铺仓库中的商品库存信息，区分在售和仓库商品。

## 使用场景

- 检查哪些商品在仓库中可上架
- 盘点库存情况
- 上架前的库存确认

## 前置条件

shop_id 通过 get_shops 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `page` | `int` | 可选 | 页码 | `1` |
| `pageSize` | `int` | 可选 | 每页数量 | `20` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | `int` | 仓库商品总数 |
| `data[]` | `array` | 商品数组，含 num_iid/title/num/status |

## 返回示例

```json
{"count":12,"data":[{"num_iid":"789012","title":"一字扣凉鞋女厚底","num":50,"status":"inventory"}]}
```

## 关联 Tool

- **后续**: `taobao_product_upshelf` — 将仓库商品上架

## 降级

MCP 不可用时: `python scripts/driver.py taobao product-inventory <shop_id>`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
