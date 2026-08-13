# taobao_trade_memo_update — 交易备注

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

添加或更新淘宝订单的卖家备注，支持旗标颜色标记（1红/2黄/3绿/4蓝/5紫）。合并了 add 和 update 两个原始 API。

## 使用场景

- 标记特殊订单（加急/赠品/换货等）
- 记录订单处理状态

## 前置条件

tid 通过 taobao_trade_list 获取

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `tid` | `string` | 必填 | 淘宝订单号 | `t1001` |
| `memo` | `string` | 必填 | 备注内容 | `客户要求发顺丰加急` |
| `flag` | `int` | 可选 | 旗标颜色: 1红/2黄/3绿/4蓝/5紫 | `1` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `tid` | `string` | 订单号 |
| `result` | `object` | 备注结果 |

## 返回示例

```json
{"tid":"t1001","result":{"status":"success"}}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao memo-add / memo-update <shop_id> <tid> <memo>`

## 常见错误

- 参考上游 API 返回的 `_hint` 字段
