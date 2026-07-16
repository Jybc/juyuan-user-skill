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

## 快速开始

1. 在[聚源发后台](https://open.jybc.com.cn)获取 API Key
2. 在 WorkBuddy 中自然说话即可：
   - **「看看今天开山网新款」** → 浏览新品
   - **「搜凉鞋」** → 搜索产品
   - **「查看我的店铺」** → 店铺列表
   - **「帮我优化标题」** → AI 标题生成 + 审核
   - **「诊断我的标题」** → SEO 深度分析
   - **「店铺仪表盘」** → 一键看概览
   - **「批量发货」** → 自动处理待发货订单
3. 首次使用会引导输入 API Key，之后全程自动

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
