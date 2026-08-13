# taobao_trade_update_address — 改地址

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

修改淘宝订单的收货地址（姓名/手机/地址）。发货后不可修改。

## 使用场景

- 买家要求修改收货地址
- 地址信息有误需要更正

## 前置条件

tid 通过 taobao_trade_list 获取，订单未发货

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `tid` | `string` | 必填 | 淘宝订单号 | `t1001` |
| `receiverName` | `string` | 必填 | 收货人姓名 | `张三` |
| `receiverPhone` | `string` | 必填 | 收货人手机号 | `13800138000` |
| `receiverAddress` | `string` | 必填 | 完整地址 | `浙江省杭州市西湖区...` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `tid` | `string` | 订单号 |
| `result` | `object` | 修改结果 |

## 返回示例

```json
{"tid":"t1001","result":{"status":"success"}}
```

## 关联 Tool

- **前置**: `taobao_trade_detail` — 查看当前地址

## 降级

MCP 不可用时: `python scripts/driver.py taobao update-address <shop_id> <tid> ...`

## 常见错误

- 已发货订单不可改地址
