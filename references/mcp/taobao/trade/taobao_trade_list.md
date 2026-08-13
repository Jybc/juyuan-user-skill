# taobao_trade_list — 订单列表

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取淘宝店铺订单列表，可按状态过滤：WAIT_SELLER_SEND_GOODS(待发货)/WAIT_BUYER_CONFIRM_GOODS(待收货)/TRADE_FINISHED(已完成)。

## 使用场景

- 查看待发货订单，准备发货
- 利润分析前拉取订单数据
- 经营日报汇总订单情况

## 前置条件

shop_id 通过 get_shops 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `status` | `string` | 可选 | 订单状态过滤 | `WAIT_SELLER_SEND_GOODS` |
| `page` | `int` | 可选 | 页码 | `1` |
| `pageSize` | `int` | 可选 | 每页数量 | `20` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | `int` | 符合条件的订单总数 |
| `data[]` | `array` | 订单数组，含 tid/num_iid/title/payment/status/buyer_nick |

## 返回示例

```json
{"count":8,"data":[{"tid":"t1001","num_iid":"789012","title":"一字扣凉鞋","payment":"88.00","status":"WAIT_SELLER_SEND_GOODS"}]}
```

## 关联 Tool

- **后续**: `taobao_trade_detail / taobao_trade_ship` — 查看订单详情 或 发货

## 降级

MCP 不可用时: `python scripts/driver.py taobao trade-list <shop_id> [status]`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
