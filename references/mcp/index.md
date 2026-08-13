# 聚源百成MCP Tool 速查索引

> 聚源百成MCP（Streamable HTTP 部署）将 jybc 后端 API 封装为 MCP Tool，供 AI 客户端（Claude/Cursor/WorkBuddy）调用。  
> 认证: 每次请求通过 `X-API-Key` header 透传 API Key，站点由 key 前缀决定。  
> 降级: MCP 不可用时，自动降级到 `python scripts/driver.py` 对应命令。

## 自定义 MCP 实例命名

每个开山网/包牛牛账户需要单独配置 API Key（内测阶段由客服提供，后续开放开山网后台/app 后台自助生成）。MCP 实例名统一用平台前缀 + 账户标识：

```
开山网0482
开山网-主账号
包牛牛-旗舰店
```

安装提示词示例：

```
请在 MCP 配置中添加：
  - 名称: 开山网0482
  - URL: https://mcp.k3.cn/mcp
  - Headers: X-API-Key=你的API密钥
```

---

## 源端 Tools（5 个）— `references/mcp/jybc/`

| MCP Tool | 上游 API | 说明 | 模块 | 文档 |
|----------|----------|------|------|------|
| `search_products` | GET /product/search | 搜索产品 | selection | [search_products.md](jybc/search_products.md) |
| `get_today_new` | GET /product/today | 今日新款 | selection | [get_today_new.md](jybc/get_today_new.md) |
| `get_shops` | GET /user/shops | 店铺列表 | selection | [get_shops.md](jybc/get_shops.md) |
| `fast_publish` | POST /product/fast-publish | 极速发布 | publish | [fast_publish.md](jybc/fast_publish.md) |
| `check_publish_result` | GET /product/fast-publish-result | 发布结果 | publish | [check_publish_result.md](jybc/check_publish_result.md) |

## 淘宝运营 Tools（25 个）— `references/mcp/taobao/`

### 店铺（2）

| MCP Tool | 上游 API | 说明 | 文档 |
|----------|----------|------|------|
| `taobao_shop_info` | GET /taobao/shop/info | 店铺基本信息 | [taobao_shop_info.md](taobao/shop/taobao_shop_info.md) |
| `taobao_seller_info` | GET /taobao/shop/seller-info | 卖家信息 | [taobao_seller_info.md](taobao/shop/taobao_seller_info.md) |

### 商品（8）

| MCP Tool | 上游 API | 说明 | 文档 |
|----------|----------|------|------|
| `taobao_product_list` | GET /taobao/product/list | 在售商品 | [product_list.md](taobao/product/taobao_product_list.md) |
| `taobao_product_detail` | GET /taobao/product/detail | 商品详情 | [product_detail.md](taobao/product/taobao_product_detail.md) |
| `taobao_product_inventory` | GET /taobao/product/inventory | 库存查询 | [product_inventory.md](taobao/product/taobao_product_inventory.md) |
| `taobao_product_update_price` | POST /taobao/product/update-price | 改价 | [update_price.md](taobao/product/taobao_product_update_price.md) |
| `taobao_product_upshelf` | POST /taobao/product/upshelf | 上架 | [upshelf.md](taobao/product/taobao_product_upshelf.md) |
| `taobao_product_downshelf` | POST /taobao/product/downshelf | 下架 | [downshelf.md](taobao/product/taobao_product_downshelf.md) |
| `taobao_product_update` | POST /taobao/product/update | 更新商品 | [update.md](taobao/product/taobao_product_update.md) |
| `taobao_product_delete` | POST /taobao/product/delete | 删除商品 ⚠ | [delete.md](taobao/product/taobao_product_delete.md) |

### 订单（6）

| MCP Tool | 上游 API | 说明 | 文档 |
|----------|----------|------|------|
| `taobao_trade_list` | GET /taobao/trade/list | 订单列表 | [trade_list.md](taobao/trade/taobao_trade_list.md) |
| `taobao_trade_detail` | GET /taobao/trade/detail | 订单详情 | [trade_detail.md](taobao/trade/taobao_trade_detail.md) |
| `taobao_trade_ship` | POST /taobao/trade/ship | 发货 ⚠ | [ship.md](taobao/trade/taobao_trade_ship.md) |
| `taobao_trade_memo_update` | POST /taobao/trade/memo/update | 交易备注 | [memo.md](taobao/trade/taobao_trade_memo_update.md) |
| `taobao_trade_update_address` | POST /taobao/trade/update-address | 改地址 | [address.md](taobao/trade/taobao_trade_update_address.md) |
| `taobao_trade_oaid_merge` | POST /taobao/trade/oaid-merge | OAID合并 | [oaid.md](taobao/trade/taobao_trade_oaid_merge.md) |

### 评价（3）

| MCP Tool | 上游 API | 说明 | 文档 |
|----------|----------|------|------|
| `taobao_rate_list` | GET /taobao/rate/list | 评价列表 | [rate_list.md](taobao/rate/taobao_rate_list.md) |
| `taobao_rate_reply` | POST /taobao/rate/reply | 评价回复 | [reply.md](taobao/rate/taobao_rate_reply.md) |
| `taobao_rate_add` | POST /taobao/rate/add | 追加评价 | [add.md](taobao/rate/taobao_rate_add.md) |

### 退款（6）

| MCP Tool | 上游 API | 说明 | 文档 |
|----------|----------|------|------|
| `taobao_refund_list` | GET /taobao/refund/receive-list | 退款列表 | [list.md](taobao/refund/taobao_refund_list.md) |
| `taobao_refund_detail` | GET /taobao/refund/detail | 退款详情 | [detail.md](taobao/refund/taobao_refund_detail.md) |
| `taobao_refund_refuse` | POST /taobao/refund/refuse | 拒绝退款 ⚠ | [refuse.md](taobao/refund/taobao_refund_refuse.md) |
| `taobao_refund_agree` | POST /taobao/refund/agree | 同意退款 ⚠ | [agree.md](taobao/refund/taobao_refund_agree.md) |
| `taobao_refund_returngoods_agree` | POST /taobao/refund/returngoods-agree | 同意退货 | [returngoods.md](taobao/refund/taobao_refund_returngoods_agree.md) |
| `taobao_refund_intercept` | POST /taobao/refund/intercept | 物流拦截 | [intercept.md](taobao/refund/taobao_refund_intercept.md) |

> ⚠ = 高风险操作，调用前需 `AskUserQuestion` 二次确认
