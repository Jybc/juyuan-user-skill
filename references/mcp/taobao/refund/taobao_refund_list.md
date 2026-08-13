# taobao_refund_list — 退款列表

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝店铺退款/售后列表，含退款状态、金额、商品信息。按状态过滤可以快速找到待处理的退款。

## 使用场景

- 查看待处理退款
- 利润分析时扣减退款金额
- 定期巡检退款情况

## 前置条件

shop_id 通过 get_shops 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `status` | `string` | 可选 | 退款状态过滤 | `WAIT_SELLER_AGREE` |
| `page` | `int` | 可选 | 页码 | `1` |
| `pageSize` | `int` | 可选 | 每页数量 | `20` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | `int` | 退款总数 |
| `data[]` | `array` | 退款数组，含 refund_id/num_iid/title/refund_fee/status |

## 返回示例

```json
{"count":2,"data":[{"refund_id":"r1001","num_iid":"789012","title":"一字扣凉鞋","refund_fee":"88.00","status":"WAIT_SELLER_AGREE"}]}
```

## 关联 Tool

- **后续**: `taobao_refund_detail` — 查看退款详情后再决定同意/拒绝

## 降级

MCP 不可用时: `python scripts/driver.py taobao refund-list <shop_id> [status]`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
