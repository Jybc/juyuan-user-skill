# get_today_new — 今日新款

> **归属模块**: `modules/selection.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取批发平台当日上新的产品列表，每天自动更新，每页 20 个产品。支持分页浏览。

## 使用场景

- 每日例行浏览新款，寻找可上架的新品
- 配合 quick-publish 一键发布当日新款

## 前置条件

已配置 `X-API-Key`（站点由 key 前缀决定）

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `page` | `int` | 可选 | 页码，从 1 开始 | `1` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `page` | `int` | 当前页码 |
| `items[]` | `array` | 产品列表，格式同 search_products 返回 |

## 返回示例

```json
{"page":1,"items":[{"id":"2001","title":"2026夏季新款松糕凉鞋","price":52.00}]}
```

## 关联 Tool

- **后续**: `fast_publish` — 选中新款后可一键发布

## 降级

MCP 不可用时: `python scripts/driver.py today [page] [platform]`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
