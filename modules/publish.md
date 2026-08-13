# 极速发布模块 (publish)

> **归属**: SKILL.md → 功能路由表 → `modules/publish.md`  
> **触发词**: 发布、极速发布、上架、publish、快发

---

## 触发词匹配

用户说出以下关键词时，加载本模块：

- `发布` / `极速发布` / `上架` / `publish` / `快发` / `一键发`

---

## MCP Tools（优先使用）

通过聚源百成MCP Streamable HTTP 调用，详见 `references/mcp/index.md`。每个 Tool 的参数和返回格式见独立文档。

| 功能 | MCP Tool | 参数文档 | 降级方案 |
|------|----------|----------|----------|
| 极速发布 | `fast_publish` | [fast_publish.md](../references/mcp/jybc/fast_publish.md) | `driver.py publish` |
| 发布结果 | `check_publish_result` | [check_publish_result.md](../references/mcp/jybc/check_publish_result.md) | `driver.py jobs` |
| 店铺列表 | `get_shops` | [get_shops.md](../references/mcp/jybc/get_shops.md) | `driver.py shops` |

**调用策略**: 优先 MCP Tool；失败/超时/不可用 → 降级 `driver.py`。

## driver.py 命令（降级路径）

### 极速发布

```bash
python scripts/driver.py publish <IDs> <shop_id> <type> [platform]
```

- `IDs`: 产品 ID，多个用逗号分隔（如 `123,456,789`）
- `shop_id`: 目标店铺 ID（先通过 `shops` 命令获取）
- `type`: 店铺类型（如 `taobao`）
- 平台: `k3`（默认）/ `bao66`

**工作流**:
1. 搜品/选品（`modules/selection.md`）
2. 确认目标店铺（`shops` 获取 shop_id）
3. 提交发布请求
4. 自动保存发布记录到 `~/.config/k3-publish/records/`

### 查询发布结果

```bash
python scripts/driver.py jobs <product_id> <shop_id> <type> [platform]
```

发布后查询任务执行状态。

### 发布记录管理

```bash
python scripts/driver.py records [date]             # 查看指定日期的发布记录
python scripts/driver.py record-list                # 列出所有发布记录文件
python scripts/driver.py export [start] [end]       # 导出 CSV 格式
```

---

## 依赖

| 类型 | 说明 |
|------|------|
| MCP Tool（优先） | `fast_publish` / `check_publish_result` / `get_shops`（`../聚源百成MCP`） |
| API（降级） | `driver.py publish` / `jobs` / `records` / `record-list` / `export` |
| 参考文档 | `references/jybc/product-fast-publish.md` / `product-fast-publish-result.md` |
