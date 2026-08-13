# taobao_trade_detail — 订单详情

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取单个订单的完整详情：收货地址、物流状态、商品清单、买家信息。发货前的必备步骤。

## 使用场景

- 发货前确认收货地址和商品信息
- 处理退款前查看订单详情

## 前置条件

tid 通过 taobao_trade_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `tid` | `string` | 必填 | 淘宝订单号 | `t1001` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `tid` | `string` | 订单号 |
| `receiver_name/phone/address` | `string` | 收货信息 |
| `orders[]` | `array` | 商品明细 |
| `payment` | `string` | 实付金额 |

## 返回示例

```json
{"tid":"t1001","receiver_name":"张三","receiver_phone":"13800138000","receiver_address":"浙江省杭州市...","payment":"88.00"}
```

## 关联 Tool

- **后续**: `taobao_trade_ship` — 确认信息后发货

## 降级

MCP 不可用时: `python scripts/driver.py taobao trade-detail <shop_id> <tid>`

## 常见错误

- tid 不存在
