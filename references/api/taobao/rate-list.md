# GET /taobao/rate/list
评价列表。
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shop_id | string | 是 | 店铺 ID |
| rate_type | string | 否 | give(给出)/get(得到)，默认 give |
| role | string | 否 | seller(卖家)/buyer(买家)，默认 seller |
| result | string | 否 | good/neutral/bad 筛选 |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页条数，默认 40，最大 150 |
| tid | string | 否 | 按订单 ID 筛选 |
| num_iid | string | 否 | 按商品 ID 筛选 |
