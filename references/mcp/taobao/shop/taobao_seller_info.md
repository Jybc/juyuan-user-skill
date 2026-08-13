# taobao_seller_info — 卖家信息

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝卖家的信用等级、经营类目、联系方式等详细信息。

## 使用场景

- 了解卖家信用和经营权限
- 检查店铺经营类目是否匹配

## 前置条件

shop_id 通过 get_shops 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `seller_nick` | `string` | 卖家昵称 |
| `level` | `int` | 信用等级 |
| `category` | `string` | 主营类目 |

## 返回示例

```json
{"seller_nick":"开山旗舰店","level":5,"category":"女鞋"}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao seller-info <shop_id>`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
