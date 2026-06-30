---
slug: juyuan-user-skill
version: 1.0.0
displayName: 聚源百成大师
description: 聚源百成大师 — 将开山网(K3)/包牛牛(Bao66)产品极速发布到淘宝、抖音、快手、拼多多等平台。支持浏览新品、搜索产品、管理店铺、追踪发布任务。
tags: [k3, 开山网, 包牛牛, 极速发布, 电商, 鞋靴]
license: MIT
homepage: https://github.com/Jybc/juyuan-user-skill
---

# 聚源百成大师

跨平台驱动，将产品从开山网(K3)和包牛牛(Bao66)发布到淘宝、抖音、快手、拼多多等电商平台。

## 交互原则

**优先用对话交互。** 获取 API Key 时用 `AskUserQuestion` 引导输入，避免让用户手动编辑配置文件。后台操作不向用户暴露终端命令细节，展示结果即可。

**不主动运行测试。** `test_driver.py` 仅供开发，正常使用时不执行。

---

## 工作流

每次使用此 skill 时，按以下顺序执行：

### 1. 环境检测

**强制使用 Python 驱动。** 只要 Python ≥ 3.8 存在，所有 API 调用必须走 `scripts/driver.py`，包括查询类操作（today/search/shops）。Python 驱动提供记录保存、分平台 Key、User-Agent 等 curl 不具备的能力。

```
python3 --version  →  有且 ≥ 3.8  →  使用 Python 驱动 (scripts/driver.py)
                    →  无/低版本
                      → curl --version  →  有 → 降级为 curl
                                         →  无 → 告知用户环境不可用
```

**curl 仅在 Python 不可用时作为最后手段**，不因「curl 也能发请求」而跳过 Python。

### 2. Config 检查

不同平台的 API Key **互不通用**，需分别配置。

读取 `~/.config/k3-publish/config` 检查目标平台的 Key：

- **已配置** → 直接进入下一步。
- **未配置** → 用 `AskUserQuestion` 弹出输入框：
  ```
  header: "API Key"
  question: "请粘贴 {平台名} 的 API Key（可在平台后台获取）"
  options: [{label: "已粘贴到输入框", description: "在上方输入框中粘贴 Key 后点击此选项"}]
  multiSelect: false
  ```
  拿到用户输入后，**静默写入 config**，不展示任何代码或路径。

  Config 格式：`API_KEY_k3=...` / `API_KEY_bao66=...`，旧格式 `API_KEY=` 作为兜底。

### 3. 功能列表

如果用户未指定具体操作，用 `AskUserQuestion` 弹出选择菜单：

```
header: "功能"
question: "你想做什么？"
options: [
  {label: "今日新款", description: "查看当天新品列表（每页 20 个）"},
  {label: "搜索产品", description: "按关键词搜索产品"},
  {label: "店铺列表", description: "查看已绑定的店铺"},
  {label: "极速发布", description: "将产品发布到店铺"},
  {label: "查看任务", description: "查询发布任务结果"},
  {label: "发布记录", description: "查看或导出历史发布记录"},
]
multiSelect: false
```

用户选择后进入步骤 4 执行。

### 4. 执行

根据用户选择，使用对应驱动命令或 curl 调用。

- API 接口详情：`references/api.md`
- curl 降级方案：`references/curl-fallback.md`
- Python 驱动用法：`scripts/driver.py`
- HTML 页面生成：`scripts/gen_apple.py`

#### 🔴 数据展示强约束（所有生成页面必须遵守）

| 约束 | 说明 |
|------|------|
| **平台标识** | 吸顶品牌栏左侧红色粗体平台名，滚动不消失 |
| **移动优先** | 默认 2 列，768px+ 变 4 列，1024px+ 变 5 列 |
| **商家&货号** | 每款产品显示一行 `商家名&货号`，不拆分 |
| **价格前置** | 价格浮在图片左下角（毛玻璃黑底），不必在卡片底部找 |
| **图片嵌入** | 产品主图下载到本地以 base64 内嵌，不用远程 URL |

#### 搜索产品完整链路

用户请求搜索时，按以下步骤静默执行：

1. `python scripts/driver.py search <关键词> [platform]` — 调用 API 搜索（注：API 要求关键词 ≥ 3 字符，2 字符时自动追加空格或关联词）
2. `python scripts/gen_apple.py search <关键词> [platform] <输出路径>` — 下载图片 + 生成 HTML 展示页
3. `present_files` — 展示生成的 HTML 页面给用户

#### 今日新款完整链路

用户请求查看新品时，按以下步骤静默执行：

1. `python scripts/driver.py today <page> [platform]` — 拉取 API 数据
2. `python scripts/gen_apple.py <page> [platform] <输出路径>` — 下载图片 + 生成 HTML 展示页
3. `present_files` — 展示生成的 HTML 页面给用户

> **注意**：不把原始 JSON 数据直接展示给用户。用户看到的是已生成的可视化页面。

## 内部参考 — 驱动命令

_以下命令仅用于后台执行，不向用户展示：_

```bash
python scripts/driver.py today [page] [platform]        # 今日新款 (原始 JSON)
python scripts/gen_apple.py <page> [platform] [out]     # 生成 HTML 展示页
python scripts/driver.py search <关键词> [platform]      # 搜索产品
python scripts/gen_apple.py search <关键词> [platform] [out] # 搜索→HTML 展示页
python scripts/driver.py shops [platform]               # 店铺列表
python scripts/driver.py publish <ID> <shop_id> <shop_type> [platform]  # 极速发布
python scripts/driver.py jobs <ID> <shop_id> <shop_type> [platform]     # 任务结果
python scripts/driver.py records [日期]                  # 发布记录
python scripts/driver.py record-list                     # 记录列表
python scripts/driver.py export [开始] [结束]             # 导出 CSV
python scripts/driver.py setup                           # 重设 API Key
```

## 平台

| 值 | 平台 |
|----|------|
| `k3` (默认) | 开山网 |
| `bao66` | 包牛牛 |
