# taobao_shop_info — 店铺基本信息

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝店铺的基本信息：店铺名称、类型、状态、开店时间等。

## 使用场景

- 查看店铺概况
- 验证 shop_id 是否有效

## 前置条件

shop_id 通过 get_shops 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `shop_name` | `string` | 店铺名称 |
| `shop_type` | `string` | 店铺类型（taobao 等） |
| `status` | `string` | 店铺状态 |

## 返回示例

```json
{"shop_name":"开山旗舰店","shop_type":"taobao","status":"open"}
```

## 关联 Tool

- **后续**: `taobao_product_list` — 查看店铺在售商品

## 降级

MCP 不可用时: `python scripts/driver.py taobao shop-info <shop_id>`

## 常见错误

- shop_id 不存在或无权限
