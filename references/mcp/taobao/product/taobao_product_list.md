# taobao_product_list — 在售商品列表

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝店铺当前在售商品列表，支持分页。返回 num_iid、标题、价格、类目等基础信息。

## 使用场景

- 浏览店铺所有在售商品
- 获取 num_iid 用于后续操作（改价/上下架/优化标题）
- 批量操作前获取商品清单

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
| `count` | `int` | 在售商品总数 |
| `data[]` | `array` | 商品数组，每项含 num_iid/title/price/cid/num |

## 返回示例

```json
{"count":45,"data":[{"num_iid":"789012","title":"一字扣凉鞋女厚底","price":"88.00","cid":50012025}]}
```

## 关联 Tool

- **后续**: `taobao_product_detail` — 查看单个商品完整详情

## 降级

MCP 不可用时: `python scripts/driver.py taobao product-list <shop_id>`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
