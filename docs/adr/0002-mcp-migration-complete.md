# ADR-0002: MCP Tool 全量迁移完成

日期: 2026-07-31
状态: Accepted

## 背景

ADR-0001 决策将单体 Skill 重构为 facade + 模块化 + MCP Server，其中 API 层采用绞杀者式迁移策略，从 `driver.py`（Python 2041 行）逐步迁移到 `聚源百成MCP` MCP Server（PHP 8.1）。

## 决策

MCP Tool 迁移采用渐进式策略，分 5 个阶段执行：

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 内部模块化拆分（SKILL.md → modules/） | 完成 |
| Phase 2 | AI 能力扩展（5 个新功能工作流） | 完成 |
| Phase 3a | selection + publish 接入 MCP（5 个已有 Tool） | 完成 |
| Phase 3b | 聚源百成MCP 开发 25 个 taobao Tool | 完成 |
| Phase 4 | taobao-ops 模块接入 MCP Tool | 完成 |
| Phase 5 | 收尾归档 | 完成 |

## 结果

### MCP Tool 清单

| 类别 | 数量 | Tool 前缀 |
|------|------|----------|
| 源端（jybc） | 5 | `search_products` / `get_today_new` / `get_shops` / `fast_publish` / `check_publish_result` |
| 淘宝运营 | 25 | `taobao_*`（店铺/商品/订单/评价/退款） |
| **合计** | **30** | |

### 架构

```
AI Agent (juyuan-user-skill)  →  MCP Server (聚源百成MCP)  →  open.jybc.com.cn (Laravel API)
        │                                  │                         │
   SKILL.md + modules/           Streamable HTTP (PHP)         Jybc 后端
        │                                  │
   降级路径: driver.py ←─────────────────┘
```

### 降级策略

- 所有 MCP Tool 标注了对应的 `driver.py` 命令作为降级路径
- `driver.py` 保留在 `scripts/` 中，MCP Server 故障时可回退
- 高风险操作（发货、退款同意/拒绝、商品删除）在 skill 端增加 `AskUserQuestion` 二次确认

## 后果

正面：
- 模块化清晰：3 个 module 文件 + 5 个 agent 文件
- API 统一：MCP Server 作为唯一 API 入口（driver.py 降级保留）
- 可扩展：新增平台只需加 3 个文件（`modules/<platform>-ops.md` + `agents/<platform>/` + `references/<platform>/`

风险：
- MCP Server 单点故障 → driver.py 作为降级路径
- MCP Tools 需在目标环境测试验证
