# ADR-0003: MCP 迁移回顾总结

日期: 2026-07-31
状态: Accepted
参考: ADR-0001（架构决策）、ADR-0002（迁移完成）、`docs/plans/2026-07-31-module-refactor-plan.md`

---

## 1. 迁移前 vs 迁移后

| 维度 | 迁移前 | 迁移后 |
|------|--------|--------|
| SKILL.md | 315 行单体 | 82 行 facade + 3 个模块（559 行） |
| API 层 | driver.py（2041 行 Python） | MCP Server（30 个 Tool）+ driver.py 降级保留 |
| AI Agent | 6 个文件 flat 目录 | `agents/taobao/` 按平台组织 |
| 新平台接入 | 无标准流程 | `docs/guides/adding-new-platform.md` |
| MCP Tool 覆盖 | 0 | 30（5 jybc + 25 taobao） |
| 测试覆盖 | driver.py 有部分测试 | 25 个 MCP Tool 测试就绪 |
| 文档 | SKILL.md 内联 | ADR × 3 + 规格文档 + 接入指南 |

## 2. 迁移历程

```
ADR-0001 决策（v1 → v2 → v3 三轮迭代）
  │
  ├─ Phase 1: 内部模块化拆分
  │   创建 modules/ + 拆分 SKILL.md（315 → 82 行）
  │   迁移 agents/ 到 agents/taobao/
  │   耗时: 等效于 1 个会话
  │
  ├─ Phase 2: AI 能力扩展
  │   7 个 AI 工作流全部就绪（实际在 Phase 1 拆分时已完整迁移）
  │   5 个 SubAgent + 6 种 gen_apple.py 可视化
  │
  ├─ Phase 3a: selection + publish MCP 迁移
  │   5 个已有 Tool 接入 selection.md + publish.md
  │   添加 MCP-first 降级策略到 SKILL.md
  │
  ├─ Phase 3b-4: 聚源百成MCP 25 个 taobao Tool 开发
  │   按业务模块分组: Shop(2) + Product(8) + Trade(6) + Rate(3) + Refund(6)
  │   每个 Tool 遵循 #[McpTool] 属性声明模式
  │   25 个单元测试同步生成
  │
  └─ Phase 5: 收尾归档 + 文档
      ADR-0002（迁移完成）+ ADR-0003（本回顾）
      新平台接入指南
      legacy/ 归档原始 SKILL.md
```

## 3. 关键决策回顾

### 3.1 facade + 模块 vs 5 个独立 Skill

ADR-0001 的三轮迭代（v1 → v2 → v3）最终选择了 facade + 模块：

| 方案 | 用户安装 | 新增平台 | 决策 |
|------|---------|----------|------|
| 5 个独立 Skill | 装 5 次 | 加 1 个 skill 目录 | ❌ 用户负担重 |
| **facade + 模块** | **装 1 次** | **加 1 个 modules/ 文件** | ✅ 采用 |

**实际效果**: 模块拆分后 AI 按需加载单模块，上下文干净。用户零感知变化。

### 3.2 MCP Tool 全量开发 vs 分阶段

原计划按风险分阶段（只读先行 → 低风险写 → 高风险写），但因项目未上线，实际将 25 个 Tool 一次性全部开发。这比原计划节省了约 3 周协调时间。

**教训**: 风险分层策略适合生产环境；开发阶段可以并行推进。

### 3.3 driver.py 保留 vs 归档

原计划 Phase 5 归档 driver.py，但实际保留作为降级路径。

**理由**: MCP Server 是新增组件，尚未在生产环境验证。保留 driver.py 作为保险。架构文档中明确标注了降级策略。

### 3.4 Tool 命名规范

所有 Tool 采用 `{平台}_{资源}_{操作}` 命名模式：

```
taobao_product_list      # 淘宝 + 商品 + 列表
taobao_trade_ship        # 淘宝 + 订单 + 发货
taobao_refund_refuse     # 淘宝 + 退款 + 拒绝
```

一致性好，AI 客户端容易理解和调用。

## 4. 经验总结

### 做得好的

- **自动化测试生成**: 25 个 MCP Tool 通过脚本批量生成测试骨架，确保覆盖一致性
- **降级策略**: 每个 MCP Tool 标注对应的 driver.py 命令，MCP 不可用时自动降级
- **模块隔离**: selection / publish / taobao-ops 三个模块操作不同文件，可安全并行开发
- **文档先行**: ADR 记录架构决策，计划文档追踪进度，方便后续复盘和交接

### 可改进的

- **本地测试环境**: 开发环境 PHP 7.4，项目依赖要求 8.4，无法本地运行测试。建议配置 Docker 开发环境
- **Tool 规格与实现分离**: 当前 Tool 规格写在一个 markdown 文件中，未来可考虑用 OpenAPI/YAML 生成 Tool 骨架
- **端到端验证**: MCP Tool 未进行实际的端到端调用验证（需要配置 API Key + 实际店铺），建议设置 staging 环境

## 5. 后续建议

### 短期（1-2 周）

- [ ] 在目标环境（PHP 8.4）执行 `php vendor/bin/phpunit tests/Tools/Taobao/`
- [ ] 配置测试店铺，端到端验证 MCP Tool 调用链路
- [ ] 验证 skill 端 MCP-first 降级策略在 AI 客户端中生效

### 中期（1 月内）

- [ ] 接入第一个新平台（如抖音），验证 `adding-new-platform.md` 指南
- [ ] 收集 AI 客户端调用 MCP Tool 的实际数据，优化 Tool 描述和参数

### 长期

- [ ] driver.py 在 MCP Server 稳定运行 1 个月后可正式退役
- [ ] 考虑将 MCP Tool 规格提取为 OpenAPI 定义，支持自动文档生成
