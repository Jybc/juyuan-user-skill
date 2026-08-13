# taobao_rate_list — 评价列表

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝店铺评价列表，支持按评价类型（收到的/发出的）、角色（买家/卖家）、评价结果（好评/中评/差评）过滤。

## 使用场景

- 差评监控：筛选 bad 查看所有差评
- 评价巡检：定期检查是否新增差评需要回复

## 前置条件

shop_id 通过 get_shops 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `rateType` | `string` | 可选 | get(收到的)/give(发出的) | `get` |
| `role` | `string` | 可选 | seller/buyer | `seller` |
| `result` | `string` | 可选 | good/neutral/bad | `bad` |
| `page` | `int` | 可选 | 页码 | `1` |
| `pageSize` | `int` | 可选 | 每页数量 | `20` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | `int` | 评价总数 |
| `data[]` | `array` | 评价数组，含 oid/content/nick/result/created |

## 返回示例

```json
{"count":3,"data":[{"oid":"o1001","content":"鞋子质量不错","nick":"买家***","result":"good"}]}
```

## 关联 Tool

- **后续**: `taobao_rate_reply` — 对差评进行回复

## 降级

MCP 不可用时: `python scripts/driver.py taobao rate-list <shop_id> [rate_type] [role] [result]`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
