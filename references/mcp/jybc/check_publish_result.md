# check_publish_result — 发布结果查询

> **归属模块**: `modules/publish.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

查询 fast_publish 提交的发布任务执行状态和结果。

## 使用场景

- fast_publish 提交后查询是否成功
- 排查发布失败原因

## 前置条件

已通过 fast_publish 提交发布任务

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `productId` | `string` | 必填 | 产品 ID | `1001` |
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `shopType` | `string` | 必填 | 店铺类型 | `taobao` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `product_id` | `string` | 发布的产品 ID |
| `result` | `object` | 发布执行结果：success/failed 及详情 |

## 返回示例

```json
{"product_id":"1001","result":{"status":"success","taobao_num_iid":"789012"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py jobs <product_id> <shop_id> <type> [platform]`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
