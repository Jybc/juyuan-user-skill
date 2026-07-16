# 聚宝 Skill

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

## 模块入口

| 模块 | 路径 | 作用 |
|------|------|------|
| API 驱动 | `scripts/driver.py` | 所有 API 调用的统一入口，1300+ 行纯 Python |
| 测试 | `scripts/test_driver.py` | 69 个单元测试，覆盖核心功能 |
| 展示页 | `scripts/gen_apple.py` | 生成移动端友好的产品展示 HTML |
| 热搜提取 | `scripts/extract_hot_keywords.py` | 从 TOP20 万词表提取热搜关键词库 |
| 标题生成 | `agents/title-generator.md` | SubAgent prompt，场景驱动 + SEO 自检 |
| SEO 诊断 | `agents/title-seo-diagnostic.md` | 四维度标题质量分析 |
| API 文档 | `references/index.md` | 34 个 API 速查索引 |
| 操作流程 | `references/common-commands.md` | 8 条常用操作流程 |
| 热搜词库 | `references/api/taobao/shoe-hot-keywords.json` | 795 个鞋靴箱包热搜词 |

命令行入口：

```bash
# 直接调用 driver
python scripts/driver.py --help                          # 全量命令列表
python scripts/driver.py search 凉鞋 k3                  # 搜索产品
python scripts/driver.py taobao dashboard 556 k3         # 店铺仪表盘
python scripts/driver.py taobao generate-titles 556 k3   # 标题数据收集
python scripts/driver.py taobao batch-price 556 +10% k3  # 批量调价

# 更新热搜词库
python scripts/extract_hot_keywords.py 淘宝TOP20万词表-无线端.xlsx
```

## 快速开始

在 WorkBuddy 中说出你的需求，聚宝自动执行：

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

## 结构

```
juyuan-user-skill/
├── SKILL.md                           # AI 工作流指引
├── README.md
├── agents/
│   ├── title-generator.md             # 标题生成 SubAgent prompt
│   ├── title-generator.schema.json    # 输出 JSON Schema
│   └── title-seo-diagnostic.md        # SEO 诊断 SubAgent prompt
├── references/
│   ├── index.md                       # API 速查索引
│   ├── common-commands.md             # 常用操作流程
│   ├── curl-fallback.md               # curl 降级方案
│   └── api/
│       ├── jybc/                      # 平台接口（5个）
│       └── taobao/
│           ├── shoe-hot-keywords.json # 鞋靴热搜词库（795词）
│           └── *.md                   # 淘宝API文档（29个）
├── scripts/
│   ├── driver.py                      # API 驱动（~1300行）
│   ├── test_driver.py                 # 单元测试（69 cases）
│   └── gen_apple.py                   # 展示页生成器
└── docs/
    └── specs/                         # 设计文档
```

## 平台

| 值 | 平台 |
|----|------|
| `k3` | 开山网（默认） |
| `bao66` | 包牛牛 |
