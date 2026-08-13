# taobao_product_downshelf — 下架

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

将在售商品下架到仓库，商品不再对外展示但数据保留。

## 使用场景

- 季节性商品过季下架
- 库存不足临时下架
- 准备更新商品信息前下架

## 前置条件

num_iid 通过 taobao_product_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `numIid` | `string` | 必填 | 商品数字 ID | `789012` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | `string` | 商品数字 ID |
| `result` | `object` | 下架结果 |

## 返回示例

```json
{"num_iid":"789012","result":{"status":"success"}}
```

## 关联 Tool

- **后续**: `taobao_product_upshelf` — 需要时可重新上架

## 降级

MCP 不可用时: `python scripts/driver.py taobao downshelf <shop_id> <num_iid>`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
