# GET /taobao/product/inventory
仓库中商品列表。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| page | int | 否 | 页码，默认 1 |
| pagesize | int | 否 | 每页条数，默认 50，最大 200 |
| cid | int | 否 | 类目筛选 |
| q | string | 否 | 关键词搜索 |
