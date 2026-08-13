# get_shops — 店铺列表

> **归属模块**: `modules/selection.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取已绑定的淘宝店铺列表，返回每个店铺的 shop_id 和 shop_type，是发布和管理的前置步骤。

## 使用场景

- 选择目标发布店铺
- 获取 shop_id 用于后续所有淘宝运营操作

## 前置条件

已在聚源百成后端绑定淘宝店铺

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| — | — | — | 无需参数 | — |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `shops[]` | `array` | 店铺列表，每项含 shop_id / shop_type / shop_name |

## 返回示例

```json
{"shops":[{"shop_id":"123456","shop_type":"taobao","shop_name":"开山旗舰店"}]}
```

## 关联 Tool

- **后续**: `fast_publish / taobao_shop_info` — 获取 shop_id 后可用于发布或店铺管理

## 降级

MCP 不可用时: `python scripts/driver.py shops [platform]`

## 常见错误

- 未绑定店铺时返回空数组
