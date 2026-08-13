# 货源搜品模块 (selection)

> **归属**: SKILL.md → 功能路由表 → `modules/selection.md`  
> **触发词**: 搜品、选品、搜索、今日新款、今天有什么、最近上什么、找货源、选款、浏览新品

---

## 触发词匹配

用户说出以下关键词时，加载本模块：

- 搜索相关: `搜索` / `搜` / `找` / `查` + 关键词
- 今日新款: `今日新款` / `今天有什么` / `最近上什么` / `新品` / `新货` / `新款`
- 选品分析: `选品` / `选款` / `逛逛` / `有什么好货`

---

## MCP Tools（优先使用）

通过聚源百成MCP Streamable HTTP 调用，详见 `references/mcp/index.md`。每个 Tool 的参数和返回格式见独立文档。

| 功能 | MCP Tool | 参数文档 | 降级方案 |
|------|----------|----------|----------|
| 搜索产品 | `search_products` | [search_products.md](../references/mcp/jybc/search_products.md) | `driver.py search` |
| 今日新款 | `get_today_new` | [get_today_new.md](../references/mcp/jybc/get_today_new.md) | `driver.py today` |
| 店铺列表 | `get_shops` | [get_shops.md](../references/mcp/jybc/get_shops.md) | `driver.py shops` |

**调用策略**: 优先 MCP Tool；失败/超时/不可用 → 降级 `driver.py`。

## driver.py 命令（降级路径）

### 搜索产品

```bash
python scripts/driver.py search <keyword> [platform]
```

- 关键词 2~20 字符，自动安全过滤
- 平台: `k3`（默认）/ `bao66`
- 展示: `gen_apple.py` 生成 HTML → `present_files` 展示

### 今日新款

```bash
python scripts/driver.py today [page] [platform]
```

- `page` 可选，默认 1
- 平台: `k3`（默认）/ `bao66`
- 展示: `gen_apple.py` 生成 HTML → `present_files` 展示

### 店铺列表

```bash
python scripts/driver.py shops [platform]
```

获取已绑定的店铺列表，为后续发布做准备。返回 `shop_id` 和 `shop_type`。

---

## 展示规则

产品列表统一走 `gen_apple.py` 渲染（`today` 或 `search` 模式）：

- 吸顶栏红色粗体平台名（`K3` / `包牛牛`）
- 移动优先：默认 2 列，768px+ → 4 列，1024px+ → 5 列
- 每款一行 `商家名&货号`
- 价格毛玻璃黑底浮于图片左下角
- 图片 base64 内嵌，不引远程 URL

---

## 依赖

| 类型 | 说明 |
|------|------|
| MCP Tool（优先） | `search_products` / `get_today_new` / `get_shops`（`../聚源百成MCP`） |
| API（降级） | `driver.py search` / `today` / `shops` |
| 可视化 | `gen_apple.py today` / `search` |
| 参考文档 | `references/jybc/product-search.md` / `product-today.md` / `user-shops.md` |
