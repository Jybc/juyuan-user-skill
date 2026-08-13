# search_products — 搜索产品

> **归属模块**: `modules/selection.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

在开山网(K3)/包牛牛(Bao66)等批发平台搜索鞋靴箱包等货源商品，返回产品列表及详细信息。

## 使用场景

- 按品类关键词搜索货源，如「凉鞋」「运动鞋」
- 批量搜品后配合 fast_publish 一键发布到淘宝

## 前置条件

已在聚源百成MCP 配置中设置正确的 `X-API-Key`（站点由 key 前缀决定，如 k3_/bao66_）

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `keyword` | `string` | 必填 | 搜索关键词 | `凉鞋` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `keyword` | `string` | 实际搜索的关键词 |
| `total` | `int` | 匹配产品总数 |
| `items[]` | `array` | 产品列表，每项含 id/title/price/img/market_price/shop_name/shop_id |

## 返回示例

```json
{"keyword":"凉鞋","total":156,"items":[{"id":"1001","title":"一字扣凉鞋女厚底","price":45.00,"img":"https://...","shop_name":"开山鞋业"}]}
```

## 关联 Tool

- **后续**: `fast_publish` — 选中产品后可一键发布

## 降级

MCP 不可用时: `python scripts/driver.py search <keyword> [platform]`

## 常见错误

- 搜索关键词 ≥ 2 字符，不足会拒绝
