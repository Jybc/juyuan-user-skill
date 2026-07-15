---
name: juyuan-user-skill
version: 1.1.0
displayName: 聚源百成大师
description: 聚源百成大师 — 将开山网(K3)/包牛牛(Bao66)产品极速发布到淘宝。支持新品浏览、搜索选品、店铺商品/订单/评价/退款管理、批量运营快捷命令。
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

## 常见问题

- **搜索关键词不够？** 需 ≥ 2 字符，超 20 自动截断。
- **店铺不存在或没有权限？** `shops` 查看已授权店铺列表。
- **网络波动报错？** 驱动自动重试 3 次，无需手动处理。
- **看不懂错误？** 响应附带 `_hint` 字段给出中文提示。
- **快捷命令？** `dashboard` 仪表盘 / `daily-report` 日报 / `auto-ship` 批量发货 / `batch-price` 批量调价 / `batch-title` 标题优化 / `title-check` 标题巡检 / `rate-check` 差评告警。完整列表见 `python scripts/driver.py --help`。
## 参考文档时效性

命令列表以 `python scripts/driver.py --help` 为唯一权威来源，始终与服务端同步。`references/api.md` 为补充说明，可能滞后于实际实现。遇到不一致时以 `--help` 输出为准。
