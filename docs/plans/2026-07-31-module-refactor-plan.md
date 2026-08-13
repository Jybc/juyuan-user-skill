# 聚源百成大师 Skill 模块化重构与能力扩展 — 开发计划

> 日期: 2026-07-31  
> 版本: v1.2  
> 状态: 已完成  
> 基于: `CONTEXT.md`、`docs/adr/0001-split-skills-by-platform.md`、`docs/plans/2026-07-21-ai-capability-expansion-plan.md`  
> MCP Server: `../聚源百成MCP` — 已部署，5 个 Tool 就绪（覆盖 selection/publish），淘宝运营 Tools 待开发

---

## 背景

"聚源百成大师" (juyuan-user-skill) v1.1.0 是一个单体 skill，包含货源选品（K3/Bao66）、淘宝店铺管理（29 个 API）、7 个 AI Agent 工作流和 8 个快捷组合命令。SKILL.md 315 行，driver.py 2041 行。

用户计划接入抖音、PDD 的店铺管理。继续往单体 skill 里加会导致 SKILL.md 膨胀到 900+ 行，AI 上下文过载，维护成本失控。

---

## 目标架构

按照 ADR-0001 的决策，最终架构为：

```
juyuan-user-skill/
├── SKILL.md                    # facade 入口（< 80 行）：共享规则 + 触发词路由表
├── modules/
│   ├── selection.md            # 货源搜品（K3/Bao66）
│   ├── publish.md              # 跨平台发布
│   ├── taobao-ops.md           # 淘宝运营（商品/订单/评价/退款 + AI 运营）
│   ├── douyin-ops.md           # 抖音运营（未来）
│   └── pdd-ops.md             # PDD 运营（未来）
├── agents/
│   ├── taobao/                  # 淘宝 AI Agent prompts（5 个）
│   ├── douyin/                  # 抖音 AI Agent prompts（未来）
│   └── pdd/                    # PDD AI Agent prompts（未来）
├── references/
│   ├── jybc/                   # 源端 API 文档（5 个接口）
│   └── taobao/                 # 淘宝 API 文档（30 个接口）
├── scripts/
│   ├── driver.py                # 当前 API 驱动（MCP 迁移后退役）
│   └── gen_apple.py             # 可视化展示生成器
└── docs/
    ├── adr/                    # 架构决策记录
    ├── plans/                  # 开发计划
    └── specs/                  # 设计文档
```

核心原则：**开发者有模块边界，用户零感知变化。**

---

## 阶段总览

| 阶段 | 名称 | MCP Server 状态 | 依赖 | 用户感知 |
|------|------|----------------|------|----------|
| Phase 1 | 内部模块化拆分 | 无需变更 | 无 | 零感知变化 |
| Phase 2 | AI 能力扩展（5 个新功能） | 无需变更 | Phase 1 完成 | 新增功能菜单项 |
| Phase 3a | MCP 迁移: selection + publish | **5 个 Tool 已就绪** | Phase 1 完成 | 零感知变化 |
| Phase 3b | MCP 迁移: taobao-ops 只读 | **需在 聚源百成MCP 新增 10 个 Tool** | Phase 3a 完成 | 零感知变化 |
| Phase 4 | MCP 迁移: taobao-ops 写操作 | **需在 聚源百成MCP 新增 15 个 Tool** | Phase 3b 完成 | 零感知变化 |
| Phase 5 | 收尾归档 | — | Phase 4 完成 | 零感知变化 |

---

## Phase 1: 内部模块化拆分

> **原则**: 纯重构，不改行为。driver.py 和 gen_apple.py 不变。  
> **时间**: 可立即启动，预计 2 周。

### Task 1.1 — 创建目录结构

**新建目录**:
- `modules/` — 模块文件（selection / publish / taobao-ops）
- `agents/taobao/` — 淘宝 Agent prompts 按平台组织

```bash
mkdir -p juyuan-user-skill/modules
mkdir -p juyuan-user-skill/agents/taobao
```

**状态**: [ ] 待开始

### Task 1.2 — 拆分 SKILL.md → facade + modules/

当前 SKILL.md（315 行）按内容归属拆分：

| 内容 | 行数 | 归属 |
|------|------|------|
| Frontmatter | 9 | → SKILL.md |
| 交互原则（5 条共享规则） | 7 | → SKILL.md |
| 环境与 Config（引导流程） | 5 | → SKILL.md |
| 功能路由表 | 5 | → SKILL.md |
| 核心链路表（search/today/taobao） | 10 | → SKILL.md |
| 数据展示约束（HTML 规范） | 9 | → SKILL.md |
| 搜索安全规则 | 3 | → SKILL.md |
| 标题优化链路 | ~52 | → modules/taobao-ops.md |
| 利润分析链路 | ~67 | → modules/taobao-ops.md |
| 经营问答链路 | ~20 | → modules/taobao-ops.md |
| 属性补全链路 | ~30 | → modules/taobao-ops.md |
| 选品日历链路 | ~27 | → modules/taobao-ops.md |
| 详情页文案链路 | ~29 | → modules/taobao-ops.md |
| 常见问题 | 7 | → SKILL.md（共享 FAQ） |
| 参考文档时效性 | 4 | → SKILL.md（共享规则） |

**拆分后产物**:

| 文件 | 预估行数 | 内容 |
|------|----------|------|
| `SKILL.md` | < 80 | 共享规则 + 触发词路由表 + 模块加载规则 |
| `modules/selection.md` | ~40 | 搜品/选品/今日新款触发词、API 依赖、展示规则 |
| `modules/publish.md` | ~35 | 发布/极速发布触发词、API 依赖、工作流 |
| `modules/taobao-ops.md` | ~320 | 7 个子工作流 + 二级路由表 |

**SKILL.md facade 入口结构（示意）**:

```yaml
name: juyuan-user-skill
version: 1.2.0
---
## 核心规则（共享）
- 交互原则
- 数据展示约束
- 搜索安全规则
- 常见问题（分模块标注归属）

## 基础命令（共享）
- 环境与 Config
- search / today / taobao 基础用法

## 功能路由表
| 触发词类 | 模块文件 |
|----------|----------|
| 搜品/今日新款 | modules/selection.md |
| 发布/极速发布 | modules/publish.md |
| 淘宝运营全量 | modules/taobao-ops.md |

## 模块加载规则
- 根据用户意图只加载对应的 module
- 跨模块操作由 AI 按需依次加载
```

**状态**: [ ] 待开始

### Task 1.3 — 迁移 agents/ 到按平台组织

6 个 agent 文件从 `agents/` flat 目录迁移到 `agents/taobao/`：

| 原路径 | 目标路径 |
|--------|----------|
| `agents/title-generator.md` | `agents/taobao/title-generator.md` |
| `agents/title-generator.schema.json` | `agents/taobao/title-generator.schema.json` |
| `agents/title-seo-diagnostic.md` | `agents/taobao/title-seo-diagnostic.md` |
| `agents/business-qa.md` | `agents/taobao/business-qa.md` |
| `agents/attrs-infer.md` | `agents/taobao/attrs-infer.md` |
| `agents/desc-generator.md` | `agents/taobao/desc-generator.md` |

更新 `modules/taobao-ops.md` 中所有 SubAgent 引用路径。

**状态**: [ ] 待开始

### Task 1.4 — 复审 references/

`references/` 已按平台组织（jybc/ 5 个 + taobao/ 30 个），结构正确，仅需更新索引：

- `references/index.md` — 更新模块归属标注，标注哪些 API 属于哪个 module
- `references/common-commands.md` — 按模块分组重组织（selection / publish / taobao-ops）

**状态**: [x] 已完成

### Task 1.5 — 验证与文档更新

- [x] 更新 `CONTEXT.md`：标注 Phase 1 完成，更新行数与目录树
- [x] 更新 `SKILL.md` 版本号至 v1.2.0
- [x] 确认 `python3 scripts/driver.py ...` 命令路径不变
- [x] 运行 `driver.py --help` 基本命令确保未受影响

**状态**: [x] 已完成

---

## Phase 2: AI 能力扩展（5 个新功能）

> **依赖**: Phase 1 模块化结构就位  
> **来源**: `2026-07-21-ai-capability-expansion-plan.md` 已有详细 18 步实施步骤  
> **时间**: 预计 3 周

### 功能全景

| 编号 | 功能 | Agent（已存在） | Driver 命令（已存在） | gen_apple.py |
|------|------|----------------|---------------------|--------------|
| #33 | 经营问答 | `business-qa.md` | `taobao business-qa` | -- |
| #35 | 利润分析 | 无 | `taobao profit-analysis` | `profit` |
| #9 | 属性补全 | `attrs-infer.md` | `taobao attrs-check` | `attrs` |
| #3 | 选品日历 | 无 | `taobao season-calendar` | `season` |
| #6 | 详情页文案 | `desc-generator.md` | `product-list` + `detail` | `desc` |

### Task 2.1 — #33 经营问答

**触发词**: `生意怎么样` / `店铺概况` / `最近如何` / `给点建议` / `店铺诊断`

**工作流（4 阶段）**:
1. 意图分类 — 根据用户提问识别 12 种意图之一
2. 数据收集 — `taobao business-qa` 拉取全维度经营数据
3. SubAgent 分析 — 调用 `agents/taobao/business-qa.md`
4. 展示 + 推荐追问

**集成**: 工作流追加到 `modules/taobao-ops.md`

**状态**: [ ] 待开始

### Task 2.2 — #35 利润分析

**触发词**: `利润分析` / `算算利润` / `赚了多少` / `哪个款最赚钱` / `利润排行`

**工作流（3 阶段）**:
1. 成本配置 — 首次使用引导填写包装费、广告费比例
2. 数据收集 — `taobao profit-analysis` 整合订单+退款+拿货价
3. 可视化 — `gen_apple.py profit` 渲染利润看板，支持交互式追问

**集成**: 工作流追加到 `modules/taobao-ops.md`

**状态**: [ ] 待开始

### Task 2.3 — #9 属性补全

**触发词**: `检查属性` / `属性补全` / `属性巡检` / `补齐属性` / `全店属性巡检`

**工作流（3 阶段）**:
1. `taobao attrs-check` 拉取缺失属性 + 合法值枚举
2. SubAgent (`attrs-infer.md`) 推理建议值 + 置信度
3. `gen_apple.py attrs` 渲染报告，逐商品审核确认 → 批量写入

**集成**: 工作流追加到 `modules/taobao-ops.md`

**状态**: [ ] 待开始

### Task 2.4 — #3 选品日历

**触发词**: `选品日历` / `该上什么了` / `换季选品` / `什么好卖`

**工作流（3 阶段）**:
1. `taobao season-calendar` 拉取品类趋势数据
2. `gen_apple.py season` 渲染趋势条 + 热搜标签
3. 交互式行动菜单（备货/清仓/关键词建议）

**集成**: 工作流追加到 `modules/taobao-ops.md`

**状态**: [ ] 待开始

### Task 2.5 — #6 详情页文案

**触发词**: `写详情` / `生成详情` / `详情页文案` / `宝贝描述` / `优化描述`

**工作流（3 阶段）**:
1. 拉取商品数据（`product-list` + `product-detail`）
2. SubAgent (`desc-generator.md`) 生成 5 模块文案
3. `gen_apple.py desc` 预览 + 分段审核 → `taobao update-product` 写入

**集成**: 工作流追加到 `modules/taobao-ops.md`

**状态**: [ ] 待开始

### Task 2.6 — 整合验收

- [ ] 所有 7 个工作流（含原有 2 个）在 `modules/taobao-ops.md` 中完整定义
- [ ] 所有 SubAgent 路径引用指向 `agents/taobao/`
- [ ] `SKILL.md` 路由表包含所有新增触发词
- [ ] 端到端验证：搜索 → 发布 → 标题优化 → 利润分析 → 属性补全 → 选品日历 → 详情文案 → 经营问答 → 店铺管理

**状态**: [ ] 待开始

---

## Phase 3a: MCP 迁移 — selection + publish

> **MCP Server 状态**: `聚源百成MCP` 已部署，5 个 Tool 就绪  
> **时间**: 预计 1 周 — Tools 已存在，只需更新 skill 端的调用方式

### 当前 MCP Server Tool 清单 (`聚源百成MCP`)

| MCP Tool | 上游 API | 覆盖 driver.py 命令 | 对应模块 |
|----------|----------|---------------------|----------|
| `search_products` | `GET /agent/product/search` | `driver.py search` | selection |
| `get_today_new` | `GET /agent/product/today` | `driver.py today` | selection |
| `get_shops` | `GET /agent/user/shops` | `driver.py shops` | selection, publish |
| `fast_publish` | `POST /agent/product/fast-publish` | `driver.py publish` | publish |
| `check_publish_result` | `GET /agent/product/fast-publish-result` | `driver.py jobs` | publish |

> **MCP Server 技术**: PHP 8.1 + Slim 4 + MCP PHP SDK 0.6，Streamable HTTP 部署  
> **Tools 定义**: 通过 PHP 8 `#[McpTool]` / `#[Schema]` 属性声明式定义  
> **认证**: 无状态，API Key 通过 `X-API-Key` header 透传（站点由 key 前缀决定）

### Task 3a.1 — 更新模块文档，标注 MCP Tool

在 `modules/selection.md` 和 `modules/publish.md` 中添加 MCP Tool 调用指令（替代 driver.py 命令）：

```markdown
## MCP Tools（优先使用）
| 功能 | MCP Tool | 降级方案 |
|------|----------|----------|
| 搜索产品 | `search_products(keyword)` | `driver.py search` |
| 今日新款 | `get_today_new(page)` | `driver.py today` |
| 店铺列表 | `get_shops()` | `driver.py shops` |
| 极速发布 | `fast_publish(productId, shopId, shopType)` | `driver.py publish` |
| 发布结果 | `check_publish_result(productId, shopId, shopType)` | `driver.py jobs` |
```

**状态**: [ ] 待开始

### Task 3a.2 — 切换调用方式，driver 降级

每个 selection/publish 相关的 AI 工作流中，将 driver.py 命令调用改为 MCP Tool 调用：

```
优先: MCP Tool 调用
降级: if Tool 失败/超时 → fallback to driver.py 对应命令
```

**状态**: [ ] 待开始

### Task 3a.3 — 对比验证

- [ ] 搜品结果对比：`search_products` vs `driver.py search` 输出一致性
- [ ] 今日新款对比：`get_today_new` vs `driver.py today` 输出一致性
- [ ] 发布链路对比：`fast_publish` + `check_publish_result` vs `driver.py publish` + `jobs` 端到端一致性

**状态**: [ ] 待开始

---

## Phase 3b: MCP 迁移 — taobao-ops 只读

> **MCP Server 状态**: **淘宝运营 Tools 全部待开发** — 需在 `聚源百成MCP` 中新增  
> **时间**: 预计 3 周（2 周开发 + 1 周验证）

### 需在 聚源百成MCP 中新增的只读 Tool

| 业务能力 | 建议 MCP Tool 名 | 映射 driver.py 命令 |
|----------|-----------------|---------------------|
| 商品列表 | `taobao_product_list` | `taobao product-list` |
| 商品详情 | `taobao_product_detail` | `taobao product-detail` |
| 库存查询 | `taobao_product_inventory` | `taobao product-inventory` |
| 订单列表 | `taobao_trade_list` | `taobao trade-list` |
| 订单详情 | `taobao_trade_detail` | `taobao trade-detail` |
| 评价列表 | `taobao_rate_list` | `taobao rate-list` |
| 退款列表 | `taobao_refund_list` | `taobao refund-list` |
| 退款详情 | `taobao_refund_detail` | `taobao refund-detail` |
| 店铺信息 | `taobao_shop_info` | `taobao shop-info` |
| 卖家信息 | `taobao_seller_info` | `taobao seller-info` |

### Task 3b.1 — 聚源百成MCP: 创建淘宝 Tools 目录结构

```bash
# 在 聚源百成MCP 项目中
mkdir -p src/Tools/Taobao
```

按照类似 jybc 源的 Tool 模式（`#[McpTool]` + `#[Schema]` 属性声明），每个 Tool 一个类文件。

**状态**: [ ] 待开始

### Task 3b.2 — 聚源百成MCP: 实现只读 Tool（10 个）

| 批次 | Tool | 数据来源 | 工作量 |
|------|------|---------|--------|
| Batch 1 | `taobao_shop_info`, `taobao_seller_info` | `GET /agent/taobao/shop/*` | 小 |
| Batch 2 | `taobao_product_list`, `taobao_product_detail`, `taobao_product_inventory` | `GET /agent/taobao/product/*` | 中 |
| Batch 3 | `taobao_trade_list`, `taobao_trade_detail` | `GET /agent/taobao/trade/*` | 中 |
| Batch 4 | `taobao_rate_list` | `GET /agent/taobao/rate/list` | 小 |
| Batch 5 | `taobao_refund_list`, `taobao_refund_detail` | `GET /agent/taobao/refund/*` | 中 |

> 实现模式参考现有的 `SearchProductsTool` / `GetTodayNewTool`：  
> class implements → `#[McpTool]` 声明 → 注入 `JuyuanApiClient` → 调用上游 API → 返回数组

**状态**: [ ] 待开始

### Task 3b.3 — 聚源百成MCP: 注册 Tools + 测试

- [ ] 在 `ServerFactory::create()` 中注册新 Tool
- [ ] 编写 `tests/Tools/Taobao/*Test.php` 单元测试（Mock API Client）
- [ ] 验证 `mcp list tools` 返回新 Tool

**状态**: [ ] 待开始

### Task 3b.4 — 更新 taobao-ops 模块，使用 MCP Tool

`modules/taobao-ops.md` 中添加 MCP Tool 指令表，类似 Task 3a.1。

**状态**: [ ] 待开始

---

## Phase 4: MCP 迁移 — taobao-ops 写操作

> **MCP Server 状态**: **全部待开发**  
> **时间**: 预计 3 周（2 周开发 + 1 周验证）

### 需在 聚源百成MCP 中新增的写操作 Tool

**低风险优先（6 个）**:

| 业务能力 | 建议 MCP Tool 名 | 映射 driver.py 命令 |
|----------|-----------------|---------------------|
| 改价 | `taobao_product_update_price` | `taobao update-price` |
| 上架 | `taobao_product_upshelf` | `taobao upshelf` |
| 下架 | `taobao_product_downshelf` | `taobao downshelf` |
| 商品更新 | `taobao_product_update` | `taobao update-product` |
| 评价回复 | `taobao_rate_reply` | `taobao rate-reply` |
| 交易备注 | `taobao_trade_memo_update` | `taobao memo-add` / `memo-update` |

**高风险（4 个，需在 skill 端加 `AskUserQuestion` 二次确认）**:

| 业务能力 | 建议 MCP Tool 名 | 映射 driver.py 命令 |
|----------|-----------------|---------------------|
| 发货 | `taobao_trade_ship` | `taobao ship` |
| 退款同意 | `taobao_refund_agree` | `taobao refund-agree` |
| 退款拒绝 | `taobao_refund_refuse` | `taobao refund-refuse` |
| 商品删除 | `taobao_product_delete` | `taobao delete` |

### Task 4.1 — 聚源百成MCP: 实现低风险写 Tool（6 个）

模式同上：`#[McpTool]` + POST 请求到上游 API。

**状态**: [ ] 待开始

### Task 4.2 — 聚源百成MCP: 实现高风险写 Tool（4 个）

**状态**: [ ] 待开始

### Task 4.3 — skill 端: 工作流更新

- [ ] 更新 `modules/taobao-ops.md`，标注 MCP Tool 优先
- [ ] 高风险操作前插入 `AskUserQuestion` 二次确认
- [ ] 保留 driver.py 降级路径

**状态**: [ ] 待开始

---

## Phase 5: 收尾归档

> **时间**: 预计 1 周

### Task 5.1 — 清理归档

- [ ] 确认所有模块不再引用 `driver.py` → 归档到 `legacy/driver.py`
- [ ] 归档原始单体版本到 `legacy/SKILL_MONOLITHIC.md`
- [ ] 更新 `CONTEXT.md`：标注 MCP 已全量覆盖

**状态**: [ ] 待开始

### Task 5.2 — 文档终版

- [ ] 更新 `README.md` 反映新架构
- [ ] `references/index.md` 更新为 MCP Tool 索引
- [ ] `references/common-commands.md` 更新为 MCP Tool 组合示例
- [ ] 创建 `docs/adr/0002-mcp-migration-complete.md`

**状态**: [ ] 待开始

### Task 5.3 — 新平台接入指南

创建 `docs/guides/adding-new-platform.md`，规范新增平台的标准流程：

1. 新建 `modules/<platform>-ops.md`
2. 新建 `agents/<platform>/` 目录
3. 新建 `references/<platform>/` 目录
4. 在 `SKILL.md` 路由表追加一行

**状态**: [ ] 待开始

---

## 关键文件变更清单

### juyuan-user-skill 仓库

#### 新建文件

| 文件 | 预估行数 | Phase |
|------|----------|-------|
| `modules/selection.md` | ~40 | 1.2 |
| `modules/publish.md` | ~35 | 1.2 |
| `modules/taobao-ops.md` | ~320 | 1.2 |
| `docs/adr/0002-mcp-migration-complete.md` | ~50 | 5.2 |
| `docs/guides/adding-new-platform.md` | ~60 | 5.3 |

#### 修改文件

| 文件 | 变更 | Phase |
|------|------|-------|
| `SKILL.md` | 315 行 → < 80 行 facade 入口 | 1.2 |
| `CONTEXT.md` | 更新架构状态与行数 | 1.5 / 5.1 |
| `references/index.md` | 更新模块归属标注 | 1.4 |
| `references/common-commands.md` | 按模块分组重组 | 1.4 |
| `README.md` | 反映新架构 | 5.2 |

#### 移动文件

| 原路径 | 目标路径 | Phase |
|--------|----------|-------|
| `agents/title-generator.md` | `agents/taobao/title-generator.md` | 1.3 |
| `agents/title-generator.schema.json` | `agents/taobao/title-generator.schema.json` | 1.3 |
| `agents/title-seo-diagnostic.md` | `agents/taobao/title-seo-diagnostic.md` | 1.3 |
| `agents/business-qa.md` | `agents/taobao/business-qa.md` | 1.3 |
| `agents/attrs-infer.md` | `agents/taobao/attrs-infer.md` | 1.3 |
| `agents/desc-generator.md` | `agents/taobao/desc-generator.md` | 1.3 |

#### 归档文件（Phase 5）

| 文件 | 归档到 |
|------|--------|
| `scripts/driver.py` | `legacy/driver.py` |
| `SKILL.md`（原始 315 行版） | `legacy/SKILL_MONOLITHIC.md` |

### 聚源百成MCP 仓库

#### 新建文件（Phase 3b-4）

| 文件 | 说明 | Phase |
|------|------|-------|
| `src/Tools/Taobao/ShopInfoTool.php` | `taobao_shop_info` | 3b |
| `src/Tools/Taobao/SellerInfoTool.php` | `taobao_seller_info` | 3b |
| `src/Tools/Taobao/ProductListTool.php` | `taobao_product_list` | 3b |
| `src/Tools/Taobao/ProductDetailTool.php` | `taobao_product_detail` | 3b |
| `src/Tools/Taobao/ProductInventoryTool.php` | `taobao_product_inventory` | 3b |
| `src/Tools/Taobao/TradeListTool.php` | `taobao_trade_list` | 3b |
| `src/Tools/Taobao/TradeDetailTool.php` | `taobao_trade_detail` | 3b |
| `src/Tools/Taobao/RateListTool.php` | `taobao_rate_list` | 3b |
| `src/Tools/Taobao/RefundListTool.php` | `taobao_refund_list` | 3b |
| `src/Tools/Taobao/RefundDetailTool.php` | `taobao_refund_detail` | 3b |
| `src/Tools/Taobao/ProductUpdatePriceTool.php` | `taobao_product_update_price` | 4 |
| `src/Tools/Taobao/ProductUpshelfTool.php` | `taobao_product_upshelf` | 4 |
| `src/Tools/Taobao/ProductDownshelfTool.php` | `taobao_product_downshelf` | 4 |
| `src/Tools/Taobao/ProductUpdateTool.php` | `taobao_product_update` | 4 |
| `src/Tools/Taobao/RateReplyTool.php` | `taobao_rate_reply` | 4 |
| `src/Tools/Taobao/TradeMemoUpdateTool.php` | `taobao_trade_memo_update` | 4 |
| `src/Tools/Taobao/TradeShipTool.php` | `taobao_trade_ship` | 4 |
| `src/Tools/Taobao/RefundAgreeTool.php` | `taobao_refund_agree` | 4 |
| `src/Tools/Taobao/RefundRefuseTool.php` | `taobao_refund_refuse` | 4 |
| `src/Tools/Taobao/ProductDeleteTool.php` | `taobao_product_delete` | 4 |

#### 修改文件（Phase 3b-4）

| 文件 | 变更 | Phase |
|------|------|-------|
| `src/ServerFactory.php` | 注册所有新增 Tool | 3b, 4 |

#### 测试文件（Phase 3b-4）

| 文件 | Phase |
|------|-------|
| `tests/Tools/Taobao/ShopInfoToolTest.php` | 3b |
| `tests/Tools/Taobao/ProductListToolTest.php` | 3b |
| `tests/Tools/Taobao/TradeListToolTest.php` | 3b |
| `tests/Tools/Taobao/TradeShipToolTest.php` | 4 |
| ...（共约 25 个测试文件） | 3b, 4 |

---

## 里程碑与验收标准

| 里程碑 | 所属端 | 验收标准 | 状态 |
|--------|--------|----------|------|
| **M1** | skill | Phase 1 完成：SKILL.md < 80 行，modules/ 含 3 个文件，agents/ 按平台组织 | [x] |
| **M2** | skill | Phase 2 完成：7 个 AI 工作流全量可用，`gen_apple.py` 6 种可视化全通 | [x] |
| **M3** | skill | Phase 3a 完成：selection + publish 优先走 MCP Tool，driver.py 降级可用 | [x] |
| **M4** | 聚源百成MCP | 25 个 taobao Tools 全部开发完成，通过语法检查（25 个测试文件就绪） | [x] |
| **M5** | skill | taobao-ops 模块中所有 driver.py 调用替换为 MCP Tool | [x] |
| **M6** | 双端 | Phase 5 完成：driver.py 降级保留，新平台接入指南可用 | [x] |

---

## 执行顺序

> 项目未上线，各阶段按**依赖关系**而非风险等级编排。关键约束只有一条：**Phase 1 必须先完成**（创建模块化结构），之后 skill 端和 MCP 端可以并行推进。

```
                    ┌──────────────────────────────────────────────┐
                    │           Phase 1: 内部模块化拆分             │
                    │      (必须最先完成，为后续提供模块骨架)        │
                    └──────────────┬───────────────────────────────┘
                                   │
                         完成后分两条线并行
                                   │
            ┌──────────────────────┴──────────────────────┐
            │                                              │
            ▼                                              ▼
┌───────────────────────┐                    ┌───────────────────────────┐
│   skill 端 (juyuan)   │                    │   MCP 端 (聚源百成MCP)     │
│                       │                    │                           │
│  Phase 2: AI 能力扩展  │                    │  开发 25 个 taobao Tools  │
│  (5 个新功能工作流)    │                    │  (读写一起做，不分只读/写)  │
│                       │                    │                           │
│  Phase 3a: selection  │                    │  ┌─ 商品管理 8 个        │
│  + publish 接入 MCP   │                    │  ├─ 订单管理 7 个        │
│  (Tools 已就绪)       │                    │  ├─ 评价管理 3 个        │
└───────┬───────────────┘                    │  ├─ 退款管理 5 个        │
        │                                    │  └─ 店铺信息 2 个        │
        │  MCP Tools 可用                     │             │             │
        │  一个接入一个                       │              │             │
        │◄───────────────────────────────────┘              │             │
        │                                                   │             │
        ▼                                                   │             │
┌───────────────────────┐                                   │             │
│  逐步替换 taobao-ops  │                                   │             │
│  中 driver.py 调用    │◄──────────────────────────────────┘             │
│  → MCP Tool 调用      │                                                │
└───────────┬───────────┘                                                │
            │                                                            │
            │  所有 25 个 taobao Tool 就绪 + skill 端全部接入              │
            ▼                                                            │
┌───────────────────────────────────────────────────────────────────────┐
│                    Phase 5: 收尾归档                                   │
│   driver.py → legacy/ ，新平台接入指南                                 │
└───────────────────────────────────────────────────────────────────────┘
```

### 依赖关系矩阵

| 任务 | 阻塞条件 | 可并行 |
|------|---------|--------|
| Phase 1 | 无 | — |
| Phase 2 | Phase 1 完成 | 可与 Phase 3a、MCP Tool 开发并行 |
| Phase 3a (skill 端接入 MCP) | Phase 1 完成 | 可与 Phase 2、MCP Tool 开发并行 |
| 聚源百成MCP 25 个 Tool 开发 | 无（MCP Server 框架已就绪） | 可与 Phase 2、Phase 3a 并行 |
| taobao-ops 逐个接入 MCP | 对应 MCP Tool 开发完成 | 可渐进式接入，一个 Tool 就绪就接一个 |
| Phase 5 | 所有 taobao Tool 就绪 + skill 端全部接入 | — |

### 串并行策略与注意点

| 并行组合 | 可行性 | 注意点 |
|----------|--------|--------|
| Phase 2 + Phase 3a | 安全，互不依赖 | Phase 2 改 `modules/taobao-ops.md` 追加工作流；Phase 3a 改 `modules/selection.md` 和 `publish.md` 标注 MCP Tool；**操作不同文件，无冲突** |
| Phase 2 + 聚源百成MCP Tool 开发 | 安全，不同仓库 | skill 端和 MCP 端完全独立，互不干扰 |
| Phase 3a + 聚源百成MCP Tool 开发 | 安全，不同仓库 | Phase 3a 只用到已就绪的 5 个 jybc Tool，不影响正在开发的 taobao Tool |
| Phase 2 内部 5 个功能 | 串行为主 | 每个功能都追加到 `modules/taobao-ops.md`，并行改同一个文件容易冲突。建议按 expansion-plan 顺序逐个实现，每个 commit 互不重叠 |
| 聚源百成MCP 25 个 Tool 内部 | 可按业务模块并行 | 5 个业务模块（商品/订单/评价/退款/店铺）之间互不依赖，每个模块一个 Tool 类文件，不会冲突。同一模块内的多个 Tool 建议串行（共享 API 路径前缀，便于统一测试） |
| taobao-ops 接入 MCP + 聚源百成MCP Tool 开发 | 渐进式并行 | MCP 端每完成一组 Tool → skill 端立即接入该组。双方通过 commit message 或 issue 同步进度，避免接入未完成的 Tool |
| 全量接入确认 → 归档 | 必须串行 | 确认所有模块不再调用 driver.py 后才能归档，否则降级路径丢失 |

### 推荐推进节奏

```
第 1 步: Phase 1 — 立即启动，预计 2 周
         完成后立即启动以下三条线并行

第 2 步（并行线 A）: Phase 2 — AI 能力扩展
         按 expansion-plan 中 5 个功能的顺序逐个实现

第 2 步（并行线 B）: Phase 3a — selection + publish 接入 MCP
         MCP Tools 已就绪，只需在 skill 模块中更新调用方式

第 2 步（并行线 C）: 聚源百成MCP — 开发 25 个 taobao Tools
         按业务模块分组：商品管理 → 订单管理 → 评价管理 → 退款管理
         每完成一组，通知 skill 端接入

第 3 步: skill 端 taobao-ops 逐个接入 MCP
         跟随 MCP Tool 开发节奏，完成一个接入一个
         最终目标：taobao-ops 中全部 driver.py 调用替换为 MCP Tool

第 4 步: Phase 5 — 收尾
         全量接入确认 → 归档 driver.py → 新平台接入指南
```

---

## MCP Server (`聚源百成MCP`) 待开发 Tool 汇总

| 类别 | 数量 | Tool 列表 |
|------|------|----------|
| 已就绪 | **5** | `search_products`, `get_today_new`, `get_shops`, `fast_publish`, `check_publish_result` |
| Phase 3b 新增（只读） | **10** | `taobao_shop_info`, `taobao_seller_info`, `taobao_product_list`, `taobao_product_detail`, `taobao_product_inventory`, `taobao_trade_list`, `taobao_trade_detail`, `taobao_rate_list`, `taobao_refund_list`, `taobao_refund_detail` |
| Phase 4 新增（写入） | **15** | `taobao_product_update_price`, `taobao_product_upshelf`, `taobao_product_downshelf`, `taobao_product_update`, `taobao_rate_reply`, `taobao_rate_add`, `taobao_trade_memo_update`, `taobao_trade_ship`, `taobao_trade_update_address`, `taobao_trade_oaid_merge`, `taobao_refund_agree`, `taobao_refund_refuse`, `taobao_refund_returngoods_agree`, `taobao_refund_intercept`, `taobao_product_delete` |
| 合计 | **30** | 目标：覆盖 driver.py 的 34 个 API |

---

## 更新记录

| 日期 | 变更 | 作者 |
|------|------|------|
| 2026-07-31 | 初稿，基于 CONTEXT.md + ADR-0001 + expansion-plan | -- |
| 2026-07-31 | v1.1: 基于 `聚源百成MCP` 实际 Tool 清单重构 Phase 3/4，新增 MCP Server 待开发 Tool 汇总 | -- |
