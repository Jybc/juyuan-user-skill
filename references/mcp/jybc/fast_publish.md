# fast_publish — 极速发布

> **归属模块**: `modules/publish.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

将批发平台的产品一键发布到淘宝店铺。支持批量发布（多个产品 ID 用逗号分隔）。发布记录自动保存到本地。

## 使用场景

- 选好产品后一键上架到淘宝店铺
- 批量发布多个选中的产品

## 前置条件

已通过 get_shops 获取 shop_id 和 shop_type

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `productId` | `string` | 必填 | 产品 ID，多个用逗号分隔 | `1001,1002,1003` |
| `shopId` | `string` | 必填 | 目标店铺 ID | `123456` |
| `shopType` | `string` | 必填 | 店铺类型 | `taobao` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `product_id` | `string` | 发布的产品 ID |
| `shop_id` | `string` | 目标店铺 ID |
| `result` | `object` | 发布结果详情 |

## 返回示例

```json
{"product_id":"1001,1002","shop_id":"123456","result":{"status":"success","message":"发布任务已提交"}}
```

## 关联 Tool

- **前置**: `get_shops` — 获取 shop_id 和 shop_type
- **后续**: `check_publish_result` — 查询发布任务执行状态

## 降级

MCP 不可用时: `python scripts/driver.py publish <IDs> <shop_id> <type> [platform]`

## 常见错误

- 店铺不存在或没有权限 → 检查 get_shops 返回的 shop_id
