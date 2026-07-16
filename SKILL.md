---
name: juyuan-user-skill
version: 1.1.0
displayName: 聚宝
description: 聚宝 — 把开山网(K3)/包牛牛(Bao66)产品一键发到淘宝。管店、改价、发货、回评、优化标题，一个skill全搞定。
tags: [k3, 开山网, 包牛牛, 极速发布, 电商, 鞋靴]
license: MIT
homepage: https://github.com/Jybc/juyuan-user-skill
---

# 聚源百成大师

将开山网(K3)/包牛牛(Bao66)产品发布到淘宝，管理商品、订单、评价、退款。

## 交互原则

- 获取 API Key 用 `AskUserQuestion` 引导，不暴露配置文件路径
- 所有操作走 `scripts/driver.py`（纯 stdlib，Python ≥ 3.8 即可）
- curl 仅在 Python 不可用时降级使用
- 不向用户展示原始 JSON，数据通过可视化页面呈现
- 驱动内置重试机制（3次指数退避），常见错误附带 `_hint` 中文提示

## 工作流

### 1. 环境与 Config

检查 Python ≥ 3.8，检查 `~/.config/k3-publish/config` 中目标平台的 Key。未配置则引导输入。

不同平台的 Key 互不通用，格式：`API_KEY_k3=...` / `API_KEY_bao66=...`

### 2. 功能选择

用户未指定操作时，弹出菜单：

- 今日新款 / 搜索产品（2~20字符，自动安全过滤）/ 店铺列表 / 极速发布 / 发布记录 / 淘宝店铺管理 / 快捷命令

### 3. 执行

API 接口详情见 `references/index.md`（按 API 逐文件拆分，按需读取）。核心链路：

| 操作 | 步骤 |
|------|------|
| **搜索** | `driver.py search` → `gen_apple.py` 生成 HTML → `present_files` 展示 |
| **今日新款** | `driver.py today` → `gen_apple.py` → `present_files` |
| **淘宝管理** | `driver.py taobao <命令>`，先 `shops` 获取 shop_id 再执行 |

#### 数据展示约束

| 约束 | 说明 |
|------|------|
| 平台标识 | 吸顶栏红色粗体平台名，滚动不消失 |
| 移动优先 | 默认 2 列，768px+ → 4 列，1024px+ → 5 列 |
| 商家&货号 | 每款一行 `商家名&货号` |
| 价格前置 | 毛玻璃黑底浮于图片左下角 |
| 图片嵌入 | base64 内嵌，不引远程 URL |

#### 搜索安全规则

关键词限制 2~20 字符：不足 2 字符拒绝+提示，超过 20 字符自动截断。输入自动去除 HTML 标签和控制字符。

#### 标题优化链路

**触发词**：`优化标题` / `优化淘宝标题` / `宝贝标题优化` / `标题优化` / `批量生成标题`

用户说这些词时，执行以下两阶段流程：

**阶段 1 — 数据收集：**
1. `python scripts/driver.py taobao generate-titles <shop_id> [platform]`
   — 拉取所有在售商品的完整属性（走 `product/detail`，含 props_name/desc/cid/price）
2. 驱动输出结构化 JSON，包含每件商品的 `num_iid` + `current_title` + `attributes` + `category` + `price` + `desc_keywords`

**阶段 2 — SubAgent 生成：**
3. 调用 Agent（`subagent_type: general-purpose`），指定 prompt 文件 `agents/title-generator.md`
4. 将阶段 1 的结构化 JSON 连同 Schema 文件 `agents/title-generator.schema.json` 一并传入
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

SubAgent prompt 和 Schema 位于 `agents/title-generator.md` / `agents/title-generator.schema.json`。

SEO 诊断 Prompt 位于 `agents/title-seo-diagnostic.md`。

**触发词**：`SEO诊断` / `标题诊断` / `分析我的标题` / `检查标题质量`

## 常见问题

- **搜索关键词不够？** 需 ≥ 2 字符，超 20 自动截断。
- **店铺不存在或没有权限？** `shops` 查看已授权店铺列表。
- **网络波动报错？** 驱动自动重试 3 次，无需手动处理。
- **看不懂错误？** 响应附带 `_hint` 字段给出中文提示。
- **快捷命令？** `dashboard` 仪表盘 / `daily-report` 日报 / `auto-ship` 批量发货 / `batch-price` 批量调价 / `batch-title` 标题优化 / `title-check` 标题巡检 / `rate-check` 差评告警。完整列表见 `python scripts/driver.py --help`。
## 参考文档时效性

命令列表以 `python scripts/driver.py --help` 为唯一权威来源，始终与服务端同步。`references/api.md` 为补充说明，可能滞后于实际实现。遇到不一致时以 `--help` 输出为准。
