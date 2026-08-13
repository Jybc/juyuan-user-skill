# 淘宝店铺运营模块 (taobao-ops)

> **归属**: SKILL.md → 功能路由表 → `modules/taobao-ops.md`  
> **功能**: 商品管理 / 订单管理 / 评价管理 / 退款管理 / AI 运营（标题优化 / SEO诊断 / 利润分析 / 经营问答 / 属性补全 / 选品日历 / 详情文案）

---

## 触发词路由（二级路由表）

| 功能类别 | 触发词 | 跳转章节 |
|----------|--------|----------|
| 标题优化 | `优化标题` / `优化淘宝标题` / `宝贝标题优化` / `批量生成标题` | #标题优化链路 |
| SEO诊断 | `SEO诊断` / `标题诊断` / `分析我的标题` / `检查标题质量` | #SEO诊断 |
| 利润分析 | `利润分析` / `算算利润` / `赚了多少` / `哪个款最赚钱` / `利润排行` / `结算一下` | #利润分析链路 |
| 经营问答 | `生意怎么样` / `店铺概况` / `最近如何` / `给点建议` / `店铺诊断` / `经营分析` | #经营问答链路 |
| 属性补全 | `检查属性` / `属性补全` / `属性巡检` / `补齐属性` / `全店属性巡检` | #属性补全链路 |
| 选品日历 | `选品日历` / `该上什么了` / `换季选品` / `秋款推荐` / `明年选品` / `什么好卖` | #选品日历链路 |
| 详情文案 | `写详情` / `生成详情` / `详情页文案` / `宝贝描述` / `生成描述` / `优化描述` | #详情页文案链路 |
| 店铺管理 | 改价、上下架、发货、退款、评���管理 | #店铺管理 |

---

## MCP Tools（优先使用）

通过聚源百成MCP Streamable HTTP 调用（`X-API-Key` 认证，站点由 key 前缀决定）。完整 Tool 清单和参数文档见 `references/mcp/index.md`。

每个 Tool 的参数和返回格式见独立文档（`references/mcp/taobao/{分组}/{tool_name}.md`）：

| 分组 | 目录 | Tool 数 |
|------|------|---------|
| 店铺 | [taobao/shop/](../references/mcp/taobao/shop/) | 2 |
| 商品 | [taobao/product/](../references/mcp/taobao/product/) | 8 |
| 订单 | [taobao/trade/](../references/mcp/taobao/trade/) | 6 |
| 评价 | [taobao/rate/](../references/mcp/taobao/rate/) | 3 |
| 退款 | [taobao/refund/](../references/mcp/taobao/refund/) | 6 |

**调用策略**: 优先 MCP Tool；失败/超时 → 降级 `driver.py`。高风险操作（发货、退款同意/拒绝、商品删除）调用前需 `AskUserQuestion` 二次确认。

---

## driver.py 命令（降级参考）

### 基础操作

淘宝店铺管理的所有命令通过 `driver.py taobao <子命令>` 执行。使用前先通过 `shops` 获取 `shop_id`。当 MCP Tool 不可用时，回退使用以下命令。

**API 接口详情见** `references/index.md`（按功能逐文件拆分，按需读取）。

**快捷命令**:
- `dashboard` — 仪表盘（多 API 汇总）
- `daily-report` — 经营日报
- `auto-ship` — 批量发货（待发货订单逐个发）
- `batch-price` — 批量调价（支持 `+10%` / `-5` / `99.00`）
- `batch-title` — 批量标题（prefix/suffix/replace）
- `title-check` — 标题质量巡检（长度/年份/重复字符）
- `rate-check` — 评价巡检/差评告警

完整命令列表见 `python scripts/driver.py --help`。

### 商品管理

| 操作 | 命令 |
|------|------|
| 商品列表 | `driver.py taobao product-list <shop_id> [platform]` |
| 库存查询 | `driver.py taobao product-inventory <shop_id> [platform]` |
| 商品详情 | `driver.py taobao product-detail <shop_id> <num_iid> [platform]` |
| 改价 | `driver.py taobao update-price <shop_id> <num_iid> <新价格> [platform]` |
| 上架 | `driver.py taobao upshelf <shop_id> <num_iid> [platform]` |
| 下架 | `driver.py taobao downshelf <shop_id> <num_iid> [platform]` |
| 更新商品 | `driver.py taobao update-product <shop_id> <num_iid> <title> <desc> [platform]` |
| 删除商品 | `driver.py taobao delete <shop_id> <num_iid> [platform]` |

### 订单管理

| 操作 | 命令 |
|------|------|
| 订单列表 | `driver.py taobao trade-list <shop_id> [status] [platform]` |
| 订单详情 | `driver.py taobao trade-detail <shop_id> <tid> [platform]` |
| 发货 | `driver.py taobao ship <shop_id> <tid> [platform]` |
| 改地址 | `driver.py taobao update-address <shop_id> <tid> <新地址> [platform]` |
| 添加备注 | `driver.py taobao memo-add <shop_id> <tid> <备注> [platform]` |
| 更新备注 | `driver.py taobao memo-update <shop_id> <tid> <备注> [platform]` |

### 评价管理

| 操作 | 命令 |
|------|------|
| 评价列表 | `driver.py taobao rate-list <shop_id> [platform]` |
| 评价回复 | `driver.py taobao rate-reply <shop_id> <oid> <回复内容> [platform]` |
| 追评 | `driver.py taobao rate-add <shop_id> <oid> <追评内容> [platform]` |

### 退款管理

| 操作 | 命令 |
|------|------|
| 退款列表 | `driver.py taobao refund-list <shop_id> [platform]` |
| 退款详情 | `driver.py taobao refund-detail <shop_id> <refund_id> [platform]` |
| 拒绝退款 | `driver.py taobao refund-refuse <shop_id> <refund_id> [理由] [platform]` |
| 同意退款 | `driver.py taobao refund-agree <shop_id> <refund_id> [platform]` |
| 同意退货 | `driver.py taobao returngoods-agree <shop_id> <refund_id> [platform]` |

---

## 标题优化链路

**触发词**: `优化标题` / `优化淘宝标题` / `宝贝标题优化` / `标题优化` / `批量生成标题`

**阶段 1 — 数据收集：**
1. `python scripts/driver.py taobao generate-titles <shop_id> [platform]`
   — 拉取所有在售商品的完整属性（走 `product/detail`，含 props_name/desc/cid/price）
2. 驱动输出结构化 JSON，包含每件商品的 `num_iid` + `current_title` + `attributes` + `category` + `price` + `desc_keywords`

**阶段 2 — SubAgent 生成：**
3. 调用 Agent（`subagent_type: general-purpose`），指定 prompt 文件 `agents/taobao/title-generator.md`
4. 将阶段 1 的结构化 JSON 连同 Schema 文件 `agents/taobao/title-generator.schema.json` 一并传入
5. SubAgent 按淘宝 SEO 规范生成新标题，输出符合 Schema 的 JSON

**阶段 3 — 用户审核：**
6. 展示新旧标题对比表，每条行尾附带操作按钮：
```
| #   | 原标题           | 建议标题                          | 分   | 操作                    |
|-----|-----------------|----------------------------------|------|------------------------|
| 1   | 厚底             | 2026夏季厚底松糕凉鞋女百搭          | 85   | [采纳] [跳过]            |
| 2   | 一字式扣带,高跟鞋 | 2026夏季真皮高跟凉鞋女一字扣带百搭   | 90   | [采纳] [跳过]            |
| 3   | 魔术贴           | 2026夏季魔术贴平底凉鞋女休闲         | 88   | [采纳] [跳过]            |
|                        底部操作： [一键采纳全部] [一键采纳高分(>85)]                         |
```
7. 每条对比用 `AskUserQuestion` 逐行确认：
```
header: "标题 {n}/{total}"
question: "【{num_iid}】 {original_title} → {generated_title} (质量分{quality_score}/{length}字)"
options: [
  {label: "采纳", description: "更新为建议标题"},
  {label: "跳过", description: "保持原标题不变"},
]
```
每行确认后立即执行 `taobao update-product`（采纳时）或跳过。
8. 也可使用底部批量选项：一键采纳全部 / 一键采纳高分(>85)，选后批量执行 update-product。

**展示修改理由**: 用户追问「为什么这么改」时，用对比表格呈现每条改动和理由，最后一行汇总共性逻辑：

```
━━━━ 原标题 → 新标题 ━━━━
改动        | 原        | 新         | 理由
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
热搜词连排   | …隔5字     | 紧贴品类词   | 连排才匹配热搜组合
品类补女     | 一字拖     | 一字拖女     | 带女搜索量碾压不带
补召回词     | (缺)       | 外穿轻奢软底  | 用满免费搜索位
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
共性逻辑: 每步都问「这个字，买家会搜吗？」搜的留，不搜的砍，漏的补。
```

### SEO诊断

SEO 诊断 Prompt 位于 `agents/taobao/title-seo-diagnostic.md`。

**触发词**: `SEO诊断` / `标题诊断` / `分析我的标题` / `检查标题质量`

---

## 利润分析链路

**触发词**: `利润分析` / `算算利润` / `赚了多少` / `哪个款最赚钱` / `利润排行` / `结算一下`

**阶段 0 — 成本配置（首次运行时）：**
1. 检查 `~/.config/k3-publish/config` 中是否存在 `COST_PACKING=xxx` 配置项
2. 不存在时用 `AskUserQuestion` 引导：
```
header: "成本配置"
question: "每单的包装和杂费大约多少？后续可在成本配置中修改。"
options: [
  {label: "¥2", description: "普通纸箱+胶带+气泡膜"},
  {label: "¥3", description: "品牌定制包装盒"},
  {label: "¥5", description: "礼盒+手提袋+贴纸"},
]
```
3. 用户选择后将值写入 `COST_PACKING=xxx` 到 config 文件
4. 继续询问是否计入广告费：
```
header: "广告费"
question: "利润分析中是否包含广告费？"
options: [
  {label: "不包含", description: "仅算成本+平台扣点"},
  {label: "包含", description: "请告诉我每月广告费总额"},
]
```
5. 选择「包含」则引导输入月均广告费，存为 `COST_AD_DAILY=xxx`（日均可分配）

**手动录入拿货价**: 对于通过发布记录无法自动匹配拿货价的商品，可使用命令：
```
python scripts/driver.py taobao set-purchase-price <shop_id> <num_iid> <价格>
```
将 num_iid→价格映射写入 `~/.config/k3-publish/records/purchase_prices.json`，后续利润分析自动读取。

**阶段 1 — 数据收集：**
1. `python scripts/driver.py taobao profit-analysis <shop_id> [platform]`
   — 拉取 TRADE_FINISHED + WAIT_BUYER_CONFIRM_GOODS 订单
   — 拉取退款数据
   — 匹配发布记录 JSON 中的拿货价（发布记录 + `purchase_prices.json` 手动映射）
   — 已配置的包装费/广告费自动纳入成本计算
   — 输出结构化文本：汇总卡片 + 利润率排行表 + **经营洞察摘要**
     · 前 3 名利润贡献比 + 核心品名
     · 低利润/亏损品告警 + 优化建议
     · 退款异常品标记
     · 缺拿货价商品提示

**阶段 2 — 可视化展示：**
2. `python scripts/gen_apple.py profit <profit_data_file> <shop_name> <output.html>`
   — 将阶段 1 的文本输出写入临时文件，传入 gen_apple.py
   — 生成包含汇总卡片 + 利润率排行表的移动端友好 HTML
3. `present_files` 展示利润看板
4. 标注缺拿货价的商品，提示用户补充

**阶段 3 — 交互追问：**
5. 展示看板后用 `AskUserQuestion` 引导深入分析：
```
header: "利润分析"
question: "还需要深入分析哪方面？"
options: [
  {label: "只看亏损商品", description: "过滤利润率偏低的商品"},
  {label: "利润趋势对比", description: "和上个月比利润变化"},
  {label: "导出报表", description: "导出CSV格式利润报表"},
  {label: "优化建议", description: "AI分析哪些品该提价或下架"},
]
```

---

## 经营问答链路

**触发词**: `生意怎么样` / `店铺概况` / `最近如何` / `给点建议` / `店铺诊断` / `经营分析`

当用户用自然语言提问且不匹配其他功能触发词时，执行智能问答：

**阶段 1 — 意图判断：**
先检查是否匹配已有功能的明确触发词（标题优化/利润分析/SEO诊断/发货/调价等），匹配则走对应链路。不匹配则进入经营问答。

**阶段 2 — 数据收集：**
1. `python scripts/driver.py taobao business-qa <shop_id> [platform]`
   — 并行拉取 5 维度概览数据（店铺/商品/订单/退款/评价），返回 JSON
2. 如有成交数据，追加 `profit-analysis` 获取利润排行和洞察

**阶段 3 — SubAgent 问答：**
3. 调用 Agent（`subagent_type: general-purpose`），prompt 使用 `agents/taobao/business-qa.md`
4. 传入 business_data(JSON) + profit_data(文本) + user_question
5. SubAgent 按意图分类 → 数据解读 → 生成回答（卡片+解读+追问）

**阶段 4 — 追问：**
6. 回答末尾附 2-3 个推荐追问；若为功能触发意图，自动跳转



---

## 属性补全链路

**触发词**: `检查属性` / `属性补全` / `属性巡检` / `补齐属性` / `全店属性巡检`

**阶段 1 — 数据收集：**
1. `python scripts/driver.py taobao attrs-check <shop_id> [platform]`
   — 拉取在售商品列表 → 逐件获取详情 (title/cid/props)
   — 通过 `taobao.itemprops.get` API 获取各类目合法属性枚举（24h 缓存）
   — 对比已有属性 vs 合法属性，找出缺失项
   — 返回结构化 JSON（缺失属性 + 候选值列表）

**阶段 2 — SubAgent 推理：**
2. 调用 Agent（`subagent_type: general-purpose`），prompt 使用 `agents/taobao/attrs-infer.md`
3. 传入阶段 1 的 JSON 结果
4. SubAgent 按标题语义提取 → 枚举值匹配 → 给出建议值和置信度
5. 如果多模态可用，下载主图做视觉验证

**阶段 3 — 审核执行：**
6. 展示属性补全报告 HTML（`gen_apple.py attrs` 模式）
7. 每条缺失属性用 `AskUserQuestion` 逐项确认：
```
header: "属性补全 {n}/{total}"
question: "【{num_iid}】{title}\n缺失: {attr_name} → 建议: {suggested_value} ({confidence}%)"
options: [
  {label: "采纳", description: "更新属性"},
  {label: "跳过", description: "保持原样"},
]
```
8. 采纳时调用 `taobao update-product` 更新 props 字段
9. 支持底部批量操作：一键采纳高置信度(>85%) / 跳过全部



---

## 选品日历链路

**触发词**: `选品日历` / `该上什么了` / `换季选品` / `秋款推荐` / `明年选品` / `什么好卖`

**阶段 1 — 数据收集：**
1. `python scripts/driver.py taobao season-calendar <shop_id> [platform]`
   — 拉取成交 + 待收货 + 待发货订单数据
   — 按标题关键词自动归类品类（凉鞋/拖鞋/单鞋/短靴/高跟鞋/帆布鞋/松糕鞋）
   — 加载热搜词库 795 词匹配品类趋势
   — 根据当前月份确定季节窗口和趋势方向
   — 输出品类趋势条图 + 行动建议

**阶段 2 — 可视化：**
2. `python scripts/gen_apple.py season <data_file> <output.html>`
   — 生成移动端友好 HTML（品类趋势条图 + 热搜关键词标签 + 行动建议卡片）
3. `present_files` 展示

**阶段 3 — 行动：**
4. 底部提供 `AskUserQuestion` 快捷操作：
```
header: "选品行动"
question: "选哪类产品开始查看？"
options: [
  {label: "提前选{{trending_cat}}"， description: "在K3/包牛牛搜索相关关键词"},
  {label: "查看更多热搜词"， description: "展示完整的热搜词库"},
  {label: "看看店铺详情"， description: "切换到经营问答看全貌"},
]
```



---

## 详情页文案链路

**触发词**: `写详情` / `生成详情` / `详情页文案` / `宝贝描述` / `生成描述` / `优化描述`

**阶段 1 — 数据准备：**
1. `python scripts/driver.py taobao product-detail <shop_id> <num_iid> [platform]`
   — 获取标题、价格、属性（建议先跑属性补全）、类目 ID
   — 如果多模态可用，下载主图做场景/色调/模特分析

**阶段 2 — SubAgent 生成：**
2. 调用 Agent（`subagent_type: general-purpose`），prompt 使用 `agents/taobao/desc-generator.md`
3. 传入 product_data + image_analysis（如有）
4. SubAgent 按价格档位确定语气 → 生成 5 模块文案（卖点/材质/场景/尺码/搭配）

**阶段 3 — 预览审核：**
5. `python scripts/gen_apple.py desc <desc_json_file> <商品标题> <output.html>`
   — 生成淘宝详情页风格的预览 HTML
6. `present_files` 展示
7. 每模块用 `AskUserQuestion` 逐项审核：
```
header: "详情页审核"
question: "卖点提炼 {n}/3: \"{selling_point}\""
options: [
  {label: "采纳", description: "保留当前文案"},
  {label: "重新生成", description: "换一个表达方式"},
  {label: "修改", description: "手动修改文案内容"},
]
```
8. 用户确认后调用 `taobao update-product` 更新 desc 字段
9. 支持一键采纳全部 / 逐模块调整



---

## 依赖

| 类型 | 说明 |
|------|------|
| MCP Tool（优先） | `taobao_*` 25 个 Tool（`../聚源百成MCP`） |
| API（降级） | `driver.py taobao *` 所有子命令 |
| SubAgent | `agents/taobao/title-generator.md` / `title-seo-diagnostic.md` / `business-qa.md` / `attrs-infer.md` / `desc-generator.md` |
| 可视化 | `gen_apple.py profit` / `attrs` / `season` / `desc` |
| 参考文档 | `references/taobao/*.md` + `references/common-commands.md` |
