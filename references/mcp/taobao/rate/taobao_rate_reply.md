# taobao_rate_reply — 评价回复

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

回复买家的评价（好评感谢或差评解释）。oid 从 rate_list 获取。

## 使用场景

- 差评回复解释
- 好评感谢回复

## 前置条件

oid 通过 taobao_rate_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `oid` | `string` | 必填 | 评价子订单号 | `o1001` |
| `reply` | `string` | 必填 | 回复内容 | `亲，感谢您的支持！有任何问题随时联系我们` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `oid` | `string` | 评价子订单号 |
| `result` | `object` | 回复结果 |

## 返回示例

```json
{"oid":"o1001","result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao rate-reply <shop_id> <oid> <reply>`

## 常见错误

- oid 不存在
- 已回复过的评价不可重复回复
