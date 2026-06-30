# 聚源发 User Skill

WorkBuddy 技能——将鞋靴产品发布到开山网（K3）和包牛牛（Bao66），支持浏览新品、搜索产品、店铺管理、极速发布、任务追踪。

## 功能

| 功能 | 说明 |
|------|------|
| 今日新款 | 查看当天新品列表，自动生成移动端友好的展示页 |
| 搜索产品 | 按关键词搜索产品，支持按货号/供应商定位 |
| 店铺列表 | 查看已绑定的店铺，获取 shop_id 和 shop_type |
| 极速发布 | 一键将产品发布到指定店铺 |
| 任务结果 | 查询发布任务状态 |
| 发布记录 | 查看或导出历史发布记录 |

## 安装

在 WorkBuddy 对话框输入以下一句话即可安装：

```
帮我安装来自 github.com/Jybc/juyuan-user-skill 的技能
```

### 国内用户

GitHub 不稳定时，用 zip 直链安装：

```
帮我安装技能 https://github.com/Jybc/juyuan-user-skill/archive/refs/heads/main.zip
```

> 依赖 Python ≥ 3.8（纯标准库，无需 pip install）

## 快速开始

1. 在[聚源发后台](https://open.jybc.com.cn)获取 API Key
2. 在 WorkBuddy 中说出你想做的事，例如：
   - 「查看开山网新款」
   - 「搜索 某个商家」
   - 「查看我的店铺」
   - 「把 商家&货号 发布到 店铺名」
3. 首次使用时会引导你输入 API Key，之后全程自动

## 结构

```
juyuan-user-skill/
├── SKILL.md                 # 工作流 + 命令速查
├── references/
│   ├── api.md               # API 文档
│   └── curl-fallback.md     # curl 降级方案
├── scripts/
│   ├── driver.py            # API 驱动
│   └── gen_apple.py         # 展示页生成器
└── README.md
```

## 平台

| 值 | 平台 |
|----|------|
| `k3` | 开山网 |
| `bao66` | 包牛牛 |
