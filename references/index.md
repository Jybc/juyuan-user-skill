# API 速查索引

> 命令语法以 `python scripts/driver.py --help` 输出为准。本索引按业务分组，指向各 API 的详细参数文件。

## 平台接口 (`api/jybc/`)

| API | 方法 | 文件 | 说明 |
|-----|------|------|------|
| /product/today | GET | [product-today.md](api/jybc/product-today.md) | 今日新款列表 |
| /product/search | GET | [product-search.md](api/jybc/product-search.md) | 搜索产品（2~20字符） |
| /user/taobao-shops | GET | [user-shops.md](api/jybc/user-shops.md) | 已绑定店铺列表 |
| /product/fast-publish | POST | [product-fast-publish.md](api/jybc/product-fast-publish.md) | 提交极速发布 |
| /product/fast-publish-result | GET | [product-fast-publish-result.md](api/jybc/product-fast-publish-result.md) | 查询发布结果 |

## 淘宝店铺管理 (`api/taobao/`)

### 店铺

| API | 方法 | 文件 | 说明 |
|-----|------|------|------|
| /taobao/shop/info | GET | [shop-info.md](api/taobao/shop-info.md) | 店铺基本信息 |
| /taobao/shop/seller-info | GET | [shop-seller-info.md](api/taobao/shop-seller-info.md) | 卖家视角信息 |
| /taobao/shop/user-info | GET | [shop-user-info.md](api/taobao/shop-user-info.md) | 卖家用户信息 |

### 商品

| API | 方法 | 文件 | 说明 |
|-----|------|------|------|
| /taobao/product/list | GET | [product-list.md](api/taobao/product-list.md) | 在售商品 |
| /taobao/product/inventory | GET | [product-inventory.md](api/taobao/product-inventory.md) | 仓库商品 |
| /taobao/product/detail | GET | [product-detail.md](api/taobao/product-detail.md) | 商品详情 |
| /taobao/product/update-price | POST | [product-update-price.md](api/taobao/product-update-price.md) | 改价 |
| /taobao/product/update | POST | [product-update.md](api/taobao/product-update.md) | 更新标题/描述 |
| /taobao/product/upshelf | POST | [product-upshelf.md](api/taobao/product-upshelf.md) | 上架 |
| /taobao/product/downshelf | POST | [product-downshelf.md](api/taobao/product-downshelf.md) | 下架 |
| /taobao/product/delete | POST | [product-delete.md](api/taobao/product-delete.md) | 删除 |

### 订单

| API | 方法 | 文件 | 说明 |
|-----|------|------|------|
| /taobao/trade/list | GET | [trade-list.md](api/taobao/trade-list.md) | 订单列表 |
| /taobao/trade/detail | GET | [trade-detail.md](api/taobao/trade-detail.md) | 订单详情 |
| /taobao/trade/ship | POST | [trade-ship.md](api/taobao/trade-ship.md) | 发货 |
| /taobao/trade/update-address | POST | [trade-update-address.md](api/taobao/trade-update-address.md) | 改地址 |
| /taobao/trade/memo/add | POST | [trade-memo-add.md](api/taobao/trade-memo-add.md) | 添加备注 |
| /taobao/trade/memo/update | POST | [trade-memo-update.md](api/taobao/trade-memo-update.md) | 更新备注 |
| /taobao/trade/oaid-merge | POST | [trade-oaid-merge.md](api/taobao/trade-oaid-merge.md) | OAID合并 |

### 评价

| API | 方法 | 文件 | 说明 |
|-----|------|------|------|
| /taobao/rate/list | GET | [rate-list.md](api/taobao/rate-list.md) | 评价列表 |
| /taobao/rate/reply | POST | [rate-reply.md](api/taobao/rate-reply.md) | 评价回复 |
| /taobao/rate/add | POST | [rate-add.md](api/taobao/rate-add.md) | 新增评价 |

### 退款

| API | 方法 | 文件 | 说明 |
|-----|------|------|------|
| /taobao/refund/receive-list | GET | [refund-receive-list.md](api/taobao/refund-receive-list.md) | 退款列表 |
| /taobao/refund/detail | GET | [refund-detail.md](api/taobao/refund-detail.md) | 退款详情 |
| /taobao/refund/refuse | POST | [refund-refuse.md](api/taobao/refund-refuse.md) | 拒绝退款 |
| /taobao/refund/agree | POST | [refund-agree.md](api/taobao/refund-agree.md) | 同意退款 |
| /taobao/refund/returngoods-agree | POST | [refund-returngoods-agree.md](api/taobao/refund-returngoods-agree.md) | 同意退货 |
| /taobao/refund/intercept | POST | [refund-intercept.md](api/taobao/refund-intercept.md) | 发起拦截 |
| /taobao/refund/deliveryintercept-feedback | POST | [refund-deliveryintercept-feedback.md](api/taobao/refund-deliveryintercept-feedback.md) | 物流拦截反馈 |
| /taobao/refund/negotiatereturn | POST | [refund-negotiatereturn.md](api/taobao/refund-negotiatereturn.md) | 协商退货退款 |

## 快捷命令

快捷命令由驱动层实现，将多个 API 组合为一步操作。完整列表见 `python scripts/driver.py --help`。

| 命令 | 说明 | 串联的 API 文件 |
|------|------|----------------|
| dashboard | 店铺仪表盘 | shop-info + product-list + trade-list + rate-list |
| daily-report | 经营日报 | 同上 + product-inventory |
| quick-publish | 快速选品发布 | product-today → fast-publish |
| auto-ship | 批量发货 | trade-list → ship × N |
| batch-price | 批量调价 | product-list → update-price × N |
| batch-title | 批量标题优化 | product-list → update × N |
| title-check | 标题质量巡检 | product-list（本地分析） |
| rate-check | 差评告警 | rate-list（筛选中差评） |
