# CONTEXT — 聚源百成大师 电商运营 Skill

> **当前状态**：facade SKILL.md（82 行）+ modules/（selection 81 行 / publish 71 行 / taobao-ops 407 行）+ driver.py（2041 行，降级保留）  
> **Phase 1-5 全部完成**，MCP Server 30 个 Tool 已就绪（5 jybc + 25 taobao）  
> **目标架构已达成**：一个 facade Skill + 按需加载的模块化内部 + MCP Server 统一 API 层  
> **核心原则**：开发者有模块边界，用户零感知变化。

---

## 货源端 (Source)
K3 / 开山网、Bao66 / 包牛牛 — 产品来源平台，通过 **jybc 后端** 的 API 提供选品数据。

## 目标端 (Target)
淘宝、抖音、PDD — 产品发布和店铺运营的目标电商平台。每个平台有独立的开放 API、SEO 规则和类目体系。

## jybc 后端
聚源百成统一 API 中间件（`http://open.jybc.com.cn/agent`）。代理所有货源端和目标端的 API，对外暴露统一接口。新增平台只需在后端加路由（`/douyin/*`、`/pdd/*`）。

## MCP Server（`../聚源百成MCP`）
已部署 Streamable HTTP MCP Server（PHP 8.1 + MCP SDK 0.6）。当前已就绪 5 个 Tool（搜品/新款/店铺/发布/发布结果），淘宝运营 25 个 Tool 待开发。

## 聚源百成大师 Skill（facade + 模块化内部）

**用户视角：** 安装一个「聚源百成大师」skill，说人话操作，不需要知道内部模块划分。

**开发者视角：** 一个入口 SKILL.md（< 80 行）路由到按需加载的模块文件。

```
juyuan-user-skill/
├── SKILL.md                    # 入口（共享交互原则 + 触发词路由表 + 展示约束）
├── modules/
│   ├── selection.md            # 货源搜索、今日新品、选品分析
│   ├── publish.md              # 从货源端发布到目标店铺（跨平台发布编排）
│   ├── taobao-ops.md           # 淘宝商品/订单/评价/退款 + 淘宝 AI 运营
│   ├── douyin-ops.md           # 抖音运营（未来）
│   └── pdd-ops.md             # PDD 运营（未来）
├── agents/
│   ├── taobao/                  # 淘宝 AI prompts（标题优化/SEO诊断/详情文案/属性补全）
│   ├── douyin/                  # 抖音 AI prompts（未来）
│   └── pdd/                    # PDD AI prompts（未来）
├── references/
│   ├── jybc/                   # 源端 API 文档（5 个接口）
│   ├── taobao/                 # 淘宝 API 文档（29 个接口）
│   ├── douyin/                 # 抖音 API 文档（未来）
│   └── pdd/                   # PDD API 文档（未来）
└── scripts/
    ├── driver.py                # 当前 API 驱动（待 MCP 迁移后淘汰）
    └── gen_apple.py             # 展示脚本（不含 API 调用）
```

### 模块加载规则

- SKILL.md 定义**触发词 → 模块文件**的映射表
- AI 根据用户意图只加载对应的 `modules/*.md`，不加载无关模块
- 跨模块操作（如"搜品→发品→优化标题"）由 AI 按需依次加载多个模块，用户无感知切换
- 新增平台只需：新建 `modules/<platform>-ops.md` + `agents/<platform>/` + `references/<platform>/`

### 模块职责边界

| 模块 | 职责 | 不负责 |
|------|------|--------|
| **selection** | K3/Bao66 搜品、今日新款、选品分析 | 发布到目标店铺、目标平台运营 |
| **publish** | 从货源产品发布到指定目标店铺 | 发布后的商品管理、订单处理 |
| **taobao-ops** | 淘宝商品/订单/评价/退款 + 淘宝 AI 运营 | 其他平台的运营、货源选品 |
| **douyin-ops** | 抖音商品/订单/售后 + 抖音 AI 运营 | 同上 |
| **pdd-ops** | PDD 商品/订单/售后 + PDD AI 运营 | 同上 |

## AI Agent
平台特定的 AI 推理 prompt。每个平台的 Agent 独立维护在 `agents/<platform>/` 下。不同平台的 Agent 不共享 SEO 规则、文案风格或属性体系。

## 极速发布
从 **货源端** 一键发布产品到 **目标端** 店铺。属于 **publish** 模块的职责。

## 店铺运营管理
**目标端** 的商品管理、订单管理、评价管理、退款管理。由对应平台的 **ops 模块**负责。

## driver.py（当前 API 驱动）
Python 实现的统一 API 调用层（2041 行），当前唯一的生产路径。计划在 MCP 完成能力对齐后淘汰，采用绞杀者式迁移。

## gen_apple.py（保留）
HTML 展示生成脚本，不含 API 调用，只管数据可视化。

## 迁移策略（已完成）
1. ~~先内部模块化（拆分 modules/ + agents/<platform>/ + references/<platform>/）~~ **Phase 1 已完成**
2. ~~AI 能力扩展（Phase 2，5 个新功能工作流）~~ **Phase 2 已完成**
3. ~~MCP 迁移：selection+publish 优先接入 5 个已就绪 Tool~~ **Phase 3a 已完成**
4. ~~聚源百成MCP 开发 25 个 taobao Tool + skill 端接入~~ **Phase 3b + 4 已完成**
5. driver.py 降级保留，MCP Server 全量覆盖后退役
