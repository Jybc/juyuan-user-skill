# taobao_product_update_price — 改价

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

修改淘宝商品售价。单次修改一个商品。批量调价使用 batch-price 快捷命令。

## 使用场景

- 单品调价
- 配合利润分析结果调整定价

## 前置条件

num_iid 通过 taobao_product_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `numIid` | `string` | 必填 | 商品数字 ID | `789012` |
| `price` | `float` | 必填 | 新价格（元） | `99.00` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | `string` | 商品数字 ID |
| `new_price` | `float` | 新价格 |
| `result` | `object` | 改价结果 |

## 返回示例

```json
{"num_iid":"789012","new_price":99,"result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao update-price <shop_id> <num_iid> <price>`

## 常见错误

- 价格不能低于类目最低限价
