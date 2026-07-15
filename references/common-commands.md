# 常用操作流程

以下为典型的日常运营场景，每个流程标注了 API 间数据传递关系。

---

## 店铺健康检查

从零感知店铺全貌，一个流程出仪表盘。

```
shops                          → 获取 shop_id
taobao shop-info <shop_id>     → 店铺基本信息
taobao product-list <shop_id>  → 在售商品数 + 最新商品
taobao trade-list <shop_id>    → 待发货 / 待收货订单数
taobao rate-list <shop_id>     → 评价概况
```

**快捷命令**：`taobao dashboard <shop_id>`

---

## 选品与发布

从批发市场选品发布到淘宝。

```
today                                 → 浏览当日新款
search <关键词>                        → 按需求搜索
shops                                 → 获取目标店铺 shop_id
fast-publish <产品ID> <shop_id> taobao → 一键发布
```

**快捷命令**：`taobao quick-publish <shop_id>`

---

## 订单发货

处理待发货订单。

```
taobao trade-list <shop_id> WAIT_SELLER_SEND_GOODS  → 获取待发货订单（tid）
taobao trade-detail <shop_id> <tid>                   → 确认订单信息
taobao ship <shop_id> <tid> <快递编码> <运单号>        → 逐笔发货
```

**快捷命令**：`taobao auto-ship <shop_id> [快递编码]`

---

## 批量调价

全场商品统一调价。

```
taobao product-list <shop_id>                  → 获取在售商品（num_iid + price）
taobao update-price <shop_id> <num_iid> <price> → 逐个改价
```

**快捷命令**：`taobao batch-price <shop_id> +10%` 或 `-5` 或 `99.00`

---

## 批量标题优化

统一优化商品标题，先看效果再执行。

```
taobao product-list <shop_id>                       → 获取所有在售标题
taobao batch-title <shop_id> suffix " 2026新款" true → 预览：加尾缀效果
taobao batch-title <shop_id> suffix " 2026新款" false → 确认后执行
taobao title-check <shop_id>                          → 最后做一轮质量巡检
```

**注意**：`batch-title` 最后一个参数 `true` 为预览模式（默认），`false` 才执行实际更新。

---

## 评价巡检与回复

监控差评并及时回复。

```
taobao rate-check <shop_id>                  → 查差评/中评告警
taobao rate-list <shop_id> get seller        → 查看具体评价内容（含 oid）
taobao rate-reply <shop_id> <oid> <回复内容>  → 逐条回复
```

---

## 退款处理

从退款列表到同意/拒绝的完整链路。

```
taobao refund-list <shop_id>                     → 获取退款列表（refund_id）
taobao refund-detail <shop_id> <refund_id>       → 查看退款详情和版本号
taobao refund-refuse <shop_id> <refund_id> <版本> "缺货无法发出" → 拒绝
# 或
taobao refund-agree <shop_id> <code> <退款JSON>   → 同意退款
```

---

## 每日经营日报

一键出当日全维度报告。

```
taobao daily-report <shop_id>
```

输出：店铺名 / 在售商品数 / 仓库商品数 / 各状态订单数 / 评价数 / 差评警告。
