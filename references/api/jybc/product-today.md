# GET /product/today

今日新款列表。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1，每页 20 条 |
| platform | string | 否 | k3 / bao66，默认 k3 |

返回字段含 `index_image`（商品主图 URL）。
