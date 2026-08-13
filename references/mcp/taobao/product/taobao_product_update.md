# taobao_product_update — 更新商品

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

更新淘宝商品信息，主要更新标题(title)和详情描述(desc)。title 和 desc 至少提供一个。用于标题优化和文案生成后的写入。

## 使用场景

- 标题优化后写入新标题
- 详情文案生成后写入新描述
- 属性补全后更新 props

## 前置条件

num_iid 通过 taobao_product_list 获取，title/desc 通过 AI 工��流生成

## 参数

| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| `shopId` | `string` | 必填 | 店铺 ID | `123456` |
| `numIid` | `string` | 必填 | 商品数字 ID | `789012` |
| `title` | `string` | 可选 | 新标题，不传则不变 | `2026夏季厚底松糕凉鞋女百搭一字扣` |
| `desc` | `string` | 可选 | 新描述，不传则不变 | `` |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | `string` | 商品数字 ID |
| `result` | `object` | 更新结果 |

## 返回示例

```json
{"num_iid":"789012","result":{"status":"success"}}
```

## 关联 Tool

- **前置**: `taobao_product_detail` — 获取原标题和属性用于 AI 生成

## 降级

MCP 不可用时: `python scripts/driver.py taobao update-product <shop_id> <num_iid> [title] [desc]`

## 常见错误

- 标题需符合淘宝规范（含违禁词会拒绝）
