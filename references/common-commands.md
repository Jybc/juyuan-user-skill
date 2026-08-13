# 常用操作流程

以下为典型的日常运营场景，按模块分组。每个流程标注了 API 间数据传递关系。

> **模块归属**: `modules/selection.md`（搜品）、`modules/publish.md`（发布）、`modules/taobao-ops.md`（淘宝运营）

---

## 货源搜品 — `modules/selection.md`

### 浏览今日新款

```
today              → 浏览当日新款（默认 k3）
today 2            → 第二页
today 1 bao66      → 包牛牛今日新款
search <关键词>     → 按需求搜索
shops              → 获取已绑定店铺列表
```

---

## 极速发布 — `modules/publish.md`

### 选品与发布

```
today                                 → 浏览当日新款（selection）
search <关键词>                        → 按需求搜索（selection）
shops                                 → 获取目标店铺 shop_id（selection）
fast-publish <产品ID> <shop_id> taobao → 一键发布
jobs <product_id> <shop_id> taobao     → 查询发布结果
```

**快捷命令**：`taobao quick-publish <shop_id>`

---

## 淘宝店铺运营 — `modules/taobao-ops.md`

### 店铺健康检查

从零感知店铺全貌，一个流程出仪表盘。

```
shops                          → 获取 shop_id
taobao shop-info <shop_id>     → 店铺基本信息
taobao product-list <shop_id>  → 在售商品数 + 最新商品
taobao trade-list <shop_id>    → 待发货 / 待收货订单数
taobao rate-list <shop_id>     → 评价概况
```

**快捷命令**：`taobao dashboard <shop_id>`

### 订单发货

处理待发货订单。

```
taobao trade-list <shop_id> WAIT_SELLER_SEND_GOODS  → 获取待发货订单（tid）
taobao trade-detail <shop_id> <tid>                   → 确认订单信息
taobao ship <shop_id> <tid> <快递编码> <运单号>        → 逐笔发货
```

**快捷命令**：`taobao auto-ship <shop_id> [快递编码]`

### 批量调价

全场商品统一调价。

```
taobao product-list <shop_id>                  → 获取在售商品（num_iid + price）
taobao update-price <shop_id> <num_iid> <price> → 逐个改价
```

**快捷命令**：`taobao batch-price <shop_id> +10%` 或 `-5` 或 `99.00`

### 批量标题优化

统一优化商品标题，先看效果再执行。

```
taobao product-list <shop_id>                       → 获取所有在售标题
taobao batch-title <shop_id> suffix " 2026新款" true → 预览：加尾缀效果
taobao batch-title <shop_id> suffix " 2026新款" false → 确认后执行
taobao title-check <shop_id>                          → 最后做一轮质量巡检
```

**注意**：`batch-title` 最后一个参数 `true` 为预览模式（默认），`false` 才执行实际更新。

### 评价巡检与回复

监控差评并及时回复。

```
taobao rate-check <shop_id>                  → 查差评/中评告警
taobao rate-list <shop_id> get seller        → 查看具体评价内容（含 oid）
taobao rate-reply <shop_id> <oid> <回复内容>  → 逐条回复
```

### 退款处理

从退款列表到同意/拒绝的完整链路。

```
taobao refund-list <shop_id>                     → 获取退款列表（refund_id）
taobao refund-detail <shop_id> <refund_id>       → 查看退款详情和版本号
taobao refund-refuse <shop_id> <refund_id> <版本> "缺货无法发出" → 拒绝
# 或
taobao refund-agree <shop_id> <code> <退款JSON>   → 同意退款
```

### 每日经营日报

一键出当日全维度报告。

```
taobao daily-report <shop_id>
```

输出：店铺名 / 在售商品数 / 仓库商品数 / 各状态订单数 / 评价数 / 差评警告。

### AI 运营工作流

| 功能 | 触发词示例 | 详见 |
|------|-----------|------|
| 标题优化 | `优化标题` / `批量生成标题` | `modules/taobao-ops.md` #标题优化链路 |
| SEO诊断 | `SEO诊断` / `标题诊断` | `modules/taobao-ops.md` #SEO诊断 |
| 利润分析 | `利润分析` / `哪个款最赚钱` | `modules/taobao-ops.md` #利润分析链路 |
| 经营问答 | `生意怎么样` / `给点建议` | `modules/taobao-ops.md` #经营问答链路 |
| 属性补全 | `检查属性` / `属性巡检` | `modules/taobao-ops.md` #属性补全链路 |
| 选品日历 | `选品日历` / `什么好卖` | `modules/taobao-ops.md` #选品日历链路 |
| 详情文案 | `写详情` / `详情页文案` | `modules/taobao-ops.md` #详情页文案链路 |
