# taobao_product_detail — 商品详情

> **归属模块**: `modules/taobao-ops.md`  
> **认证**: 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

## 简述

获取单个商品的完整详细信息：属性(props_name)、描述(desc)、类目(cid)、价格、图片等。标题优化和文案生成的核心数据来源。

## 使用场景

- 标题优化前获取商品属性进行分析
- 详情文案生成前获取完整商品信息
- 属性补全前检查已有属性

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
| `title` | `string` | 当前标题 |
| `props_name` | `string` | 商品属性（格式: 品牌:A;跟型:B） |
| `desc` | `string` | 详情页描述 |
| `cid` | `string` | 商品类目 ID |
| `price` | `string` | 当前售价 |

## 返回示例

```json
{"num_iid":"789012","title":"一字扣凉鞋女厚底","props_name":"品牌:百丽;跟型:松糕底;闭合方式:一字式扣带","cid":"50012025","price":"88.00","desc":"..."}
```

## 关联 Tool

- 无强关联

## 降级

MCP 不可用时: `python scripts/driver.py taobao product-detail <shop_id> <num_iid>`

## 常见错误

- num_iid 不存在或已下架
