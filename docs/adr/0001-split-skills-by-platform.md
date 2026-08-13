# ADR-0001: 从单体 Skill 到 facade + 模块化 + MCP

日期: 2026-07-31（初稿 → 复审 → 终稿）
状态: Accepted

## 迭代记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 07-31 | 初稿：按平台拆 5 个独立 Skill，MCP 全管 API，淘汰 driver，全量重写 |
| v2 | 07-31 | 复审修正：撤销"driver 已废弃"��"全量重写"，改为绞杀者迁移 |
| v3 | 07-31 | 终稿：改为 1 个 facade Skill + 模块化内部，用户零感知变化 |

---

## 背景

"聚源百成大师" (juyuan-user-skill) v1.1.0 是一个单体 skill，包含货源选品（K3/Bao66）、淘宝店铺管理（29 个 API）、7 个 AI Agent 工作流和 8 个快捷组合命令。SKILL.md 315 行，driver.py 2041 行。

用户计划接入抖音、PDD 的店铺管理。如果继续往单体 skill 里加，SKILL.md 将膨胀到 900+ 行，AI 上下文过载，维护成本失控。

## 决策

### 架构形态

| 维度 | 决策 |
|------|------|
| **用户视角** | 安装一个「聚源百成大师」skill，说人话操作，不知道内部模块划分 |
| **开发者视角** | 1 个入口 SKILL.md（< 80 行）+ 按需加载的 modules/ + 按平台隔离的 agents/ |
| **SKILL.md** | 只放共享交互原则、触发词→模块路由表、数据展示约束 |
| **模块** | `modules/selection.md` / `publish.md` / `taobao-ops.md` + 未来平台 |
| **AI Agent** | `agents/<platform>/` 下各自独立维护，不同平台不共享 |
| **API 调用** | 当前 driver.py → 目标 MCP Server（绞杀者迁移） |
| **展示层** | gen_apple.py 保留，不含 API 调用 |

### 为什么选 facade + 模块而不是 5 个独立 Skill

| 方案 | 用户安装 | AI 上下文 | 新增平台 | 用户感知变化 |
|------|---------|----------|---------|-------------|
| 5 个独立 Skill | 装 5 次 | 单 skill 上下文干净 | 加 1 个新 skill 目录 | 需了解多个 skill |
| **facade + 模块** | **装 1 次** | **按需加载单模块** | **加 1 个 modules/ 文件** | **零感知变化** |

结论：模块边界是开发者要的东西，不应该让用户买单。

### 模块职责

```
selection (货源搜品) ──→ publish (跨平台发布) ──→ taobao-ops (淘宝运营)
                                                      │
                                                    douyin-ops (未来)
                                                    pdd-ops (未来)
```

每个模块文件只定义该模块的：
- 触发词
- 工作流步骤
- 依赖的 MCP Tool 或 driver 命令
- 数据展示规则

### API 层

- **当前**：`scripts/driver.py`（2041 行），直连 jybc 后端，唯一生产路径
- **目标**：MCP Server（服务器端 Streamable HTTP），Tool 按业务能力封装
- **迁移**：绞杀者模式，5 阶段逐步切换（详见下方）

### 迁移路线

```
Phase 1: 内部模块化（零风险，立即可做）
  - 拆分 modules/ + agents/<platform>/ + references/<platform>/
  - SKILL.md 瘦身为路由表
  - driver.py 不变，gen_apple.py 不变
  - 用户零感知

Phase 2: MCP 只读迁移
  - MCP 先实现 shops / product-list / trade-list / rate-list / refund-list
  - modules/ 中对应模块改为调 MCP Tool
  - 新旧并存，对比验证

Phase 3: MCP 低风险写迁移
  - 改价、上下架、标题更新、评价回复、交易备注

Phase 4: MCP 高风险写迁移
  - 发货、退款同意/拒绝、商品删除
  - 增加确认环节

Phase 5: 收尾
  - 全量 MCP 覆盖且稳定 → 归档 driver.py
```

### MCP Tool 设计原则

- 按**业务能力**封装（如 `taobao_get_pending_shipments`），不逐条暴露原始 HTTP 端点
- 复杂工作流（标题优化全链路）保留在 modules/ 中，MCP 只负责数据读写
- 支付相关 Tool 独立部署（独立 MCP Server 或独立 connector），不与电商 Tool 混用

## 理由

- 淘宝、抖音、PDD 的 SEO 规则、类目体系、数据结构完全不同，共用 Agent prompt 不现实
- 单体 skill 已到瓶颈：SKILL.md 315 行，加一个平台就膨胀 200+ 行
- facade + 模块是唯一同时满足「用户简单」和「开发者可维护」的方案
- 内部模块化是零风险的纯重构，不改变任何对外行为
- MCP 长期降低分发门槛，但必须验证后才能切换

## 后果

正面：
- 用户仍然只装一个 skill，操作链路不变
- 开发者有清晰的模块边界，新增平台不碰旧代码
- AI 按需加载单模块，上下文干净
- 内部模块化可立即启动，无需等 MCP

负面：
- 需要维护模块划分的纪律（防止模块间隐式耦合）
- 过渡期 driver.py 和 MCP 双路径并存
- modules/ 文件增多后需做好命名和组织规范

风险：
- MCP 服务器单点故障 → driver.py 作为降级路径，迁移期间不删除
- 模块职责边界模糊 → 用上表严格约束，review 时检查
