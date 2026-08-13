# 聚源百成大师 Skill

把开山网（K3）/ 包牛牛（Bao66）的产品一键发到淘宝。管店、改价、发货、回评、优化标题，一个 skill 全搞定。

## 核心能力

### 选品发布
| 功能 | 说明 |
|------|------|
| 今日新款 | 查看当日新品，自动生成移动端展示页 |
| 搜索产品 | 按关键词搜索（2~20字符），自动安全过滤 |
| 极速发布 | 一键将产品发布到淘宝店铺 |
| 发布记录 | 查看/导出历史发布记录 |

### 店铺管理
| 功能 | 说明 |
|------|------|
| 商品管理 | 在售/仓库商品列表、上下架、改价、删除 |
| 订单管理 | 订单列表/详情、发货、改地址、备注 |
| 评价管理 | 评价列表、回复、差评告警 |
| 退款管理 | 退款列表、同意/拒绝、退货、拦截 |

### 批量运营
| 命令 | 说明 |
|------|------|
| `dashboard` | 店铺仪表盘，一键看全貌 |
| `daily-report` | 每日经营日报 |
| `auto-ship` | 批量发货待处理订单 |
| `batch-price` | 批量调价（+10% / -5 / 99.00） |
| `batch-title` | 批量标题优化（prefix/suffix/replace） |

### AI 能力
| 功能 | 说明 |
|------|------|
| 标题优化 | 场景驱动 + 热搜词库 + SEO 自检，生成符合2026淘宝算法的标题 |
| SEO 诊断 | 四维度分析：热搜覆盖 / 词序评分 / 竞争分析 / 改进建议 |

## MCP 接入（主路径）

本 Skill 优先通过 **聚源百成MCP** 服务端（Streamable HTTP，30 个 Tool）调用业务能力。每个账户在 AI 客户端中配置一个独立 MCP 实例。

| 项目 | 值 |
|------|-----|
| 服务地址 | `https://mcp.k3.cn/mcp`（服务端：聚源百成MCP） |
| 认证 | 请求头 `X-API-Key`（站点由 key 前缀决定，如 `k3_xxx` → 开山网） |
| 实例命名 | `开山网{账号}` / `包牛牛{账号}`（如 `开山网0482`） |
| Tool 数 | 30 = 源端 5 + 淘宝运营 25 |
| API token | 内测阶段由客服提供（后续开放开山网后台/app 后台自助生成） |

### MCP 就绪检查

安装 Skill 后，AI 会先检查本地 MCP 配置（`~/.workbuddy/mcp.json`、`~/.claude.json` 等）是否有实例名以 `开山网*` / `包牛牛*` 前缀命名的连接：

- **有** → 直接开始使用
- **没有** → 提示用户：「当前未配置开山网/包牛牛 MCP，内测阶段请联系客服索取你的 API token」，并提供下方配置引导

### 配置 mcp.json

用户将客服提供的 mcp.json 配置粘贴给 AI，由 AI 写入 `~/.workbuddy/mcp.json` 并引导信任：

```json
{
  "mcpServers": {
    "开山网****": {
      "url": "https://mcp.k3.cn/mcp",
      "headers": {
        "X-API-Key": "k3_************************"
      }
    }
  }
}
```

> 安装助手：内置 **聚源百成 MCP 安装助手** skill（`mcp.k3.cn/install-skill`）。说「帮我配置开山网 MCP」，它会自动写入 `mcp.json` 并引导到连接器管理页信任。

### Tool 概览

**源端 5 个**（`references/mcp/jybc/`）：`search_products` / `get_today_new` / `get_shops` / `fast_publish` / `check_publish_result`

**淘宝运营 25 个**（`references/mcp/taobao/`）：

| 分组 | Tool 数 | 文档目录 |
|------|--------|----------|
| 店铺 | 2 | `references/mcp/taobao/shop/` |
| 商品 | 8 | `references/mcp/taobao/product/` |
| 订单 | 6 | `references/mcp/taobao/trade/` |
| 评价 | 3 | `references/mcp/taobao/rate/` |
| 退款 | 6 | `references/mcp/taobao/refund/` |

完整清单与参数见 `references/mcp/index.md`。标记 ⚠ 的高风险操作（发货 / 删除 / 退款同意 / 拒绝）调用前需二次确认。

## driver.py 降级（备用路径）

MCP 不可用时自动降级 `scripts/driver.py`（2041 行，Python 3.8+ 标准库），curl 仅在无 Python 时兜底。

```bash
python scripts/driver.py --help                          # 全量命令列表（唯一权威来源）
python scripts/driver.py search 凉鞋 k3                  # 搜索产品
python scripts/driver.py taobao dashboard 556 k3         # 店铺仪表盘
python scripts/driver.py taobao batch-price 556 +10% k3  # 批量调价
```

## 安装

在 WorkBuddy 中输入：

```
帮我安装来自 github.com/Jybc/juyuan-user-skill 的技能
```

国内用户（GitHub 不稳定时）：

```
帮我安装技能 https://github.com/Jybc/juyuan-user-skill/archive/refs/heads/main.zip
```

> 依赖 Python ≥ 3.8，纯标准库，无需 pip install

## 快速开始

在 WorkBuddy 中说出你的需求，聚源百成大师自动执行：

| 你想做什么 | 这样说 |
|-----------|--------|
| 看今天新款 | 「看看开山网今天新款」「有新品吗」 |
| 搜产品 | 「搜凉鞋」「找一个厚底拖鞋」「搜货号 xxx」 |
| 发品到店铺 | 「把这个发到xx店铺」「上架到我的店铺」 |
| 改全店价格 | 「全场 9 折」「全部涨价 5 块」 |
| 处理待发货 | 「帮我发货」「待发货的单子都发了」 |
| 看店铺情况 | 「仪表盘」「今天日报」「店铺怎么样了」 |
| 优化标题 | 「帮我优化标题」「宝贝标题生成一下」 |
| 检查标题 | 「诊断我的标题」「SEO 分析一下」 |
| 看差评 | 「有没有差评」「评价巡检」 |
| 处理退款 | 「看看退款」「同意这笔退款」 |

首次使用会引导输入 API Key，之后全程自动。

## 可靠性

- 网络波动自动重试 3 次（指数退避）
- 常见错误附带中文 `_hint` 提示
- 搜索词自动安全过滤（去 HTML 标签和控制字符）
- 命令列表以 `python scripts/driver.py --help` 为唯一权威来源，`references/` 为补充说明，不一致时以 `--help` 为准

## 结构

```
juyuan-user-skill/
├── SKILL.md                           # AI 工作流指引（facade 入口）
├── README.md
├── modules/
│   ├── selection.md                   # 货源搜品
│   ├── publish.md                     # 极速发布
│   └── taobao-ops.md                  # 淘宝店铺运营
├── agents/taobao/                     # 淘宝 AI SubAgent（6 个 prompt + schema）
├── references/
│   ├── index.md                       # API 速查索引
│   ├── common-commands.md             # 常用操作流程
│   ├── curl-fallback.md               # curl 降级方案
│   ├── api/jybc/                      # 平台接口（5个）
│   ├── api/taobao/                    # 淘宝API文档（29个 + 热搜词库 795 词）
│   └── mcp/                           # MCP Tool 文档（index + jybc 5 + taobao 25）
├── scripts/
│   ├── driver.py                      # 降级 API 驱动（2041 行）
│   ├── test_driver.py                 # 单元测试（79 cases）
│   └── gen_apple.py                   # 展示页生成器（765 行，无 API 调用）
└── docs/                              # adr / plans / specs / guides
```

## 平台

站点由 API Key 前缀决定（仅 MCP 路径）：

| 前缀 | 平台 |
|------|------|
| `k3` | 开山网 |
| `bao66` | 包牛牛 |
| `juyi5` | 聚衣网 |
| `2tong` | 二童网 |
| `yoduo` | 有多网 |
| `xingfujie` | 幸福街 |
| `xyk3` | 新余开山网 |

> driver.py 降级路径仅支持 `k3` / `bao66`。
