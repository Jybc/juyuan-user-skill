# taobao_trade_ship — 发货

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

> ⚠️ 高风险操作 — 调用前需 `AskUserQuestion` 二次确认

## 简述

⚠️ 对淘宝订单进行发货操作，填写快递公司和运单号。物流信息不可逆。调用前需二次确认。

## 使用场景

- 确认订单信息后发货
- 批量发货（配合 auto-ship）

## 前置条件

tid 通过 taobao_trade_list 获取，先通过 trade_detail 确认收货地址

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `tid` | `string` | 必填 | 淘宝订单号 | `t1001` |
| `express` | `string` | 必填 | 快递公司编码（STO/ZTO/YUNDA/SF/EMS） | `STO` |
| `trackNo` | `string` | 必填 | 快递运单号 | `7730123456789` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `tid` | `string` | 订单号 |
| `express` | `string` | 快递公司 |
| `track_no` | `string` | 运单号 |
| `result` | `object` | 发货结果 |

## 返回示例

```json
{"tid":"t1001","express":"STO","track_no":"7730123456789","result":{"status":"success"}}
```

## 关联 Tool

- **前置**: `taobao_trade_detail` — 确认收货地址无误

## 降级

MCP 不可用时: `python scripts/driver.py taobao ship <shop_id> <tid> <express> <track_no>`

## 常见错误

- 运单号无效或已被使用
- 订单状态不允许发货
