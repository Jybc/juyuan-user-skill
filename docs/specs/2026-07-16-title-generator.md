# 淘宝标题批量生成器 — 设计文档

**日期**: 2026-07-16
**状态**: Draft

## 1. 概述

在售商品的原标题通常简短且缺少 SEO 关键词（如 `"厚底"`、`"魔术贴"`），影响淘宝搜索曝光。本功能通过 SubAgent 读取商品完整属性 + 商家描述，自动生成符合淘宝规范的高质量标题。

## 2. 数据流

```
driver.py                       SubAgent                    淘宝 API
─────────                       ────────                    ────────
product/list  ──→ num_iid × N
product/detail × N ──→ 属性 JSON    ──→ title-generator
                                       ├── 解析属性 → 关键词
                                       ├── 保留原标题词
                                       ├── 拼装 SEO 标题
                                       └── 输出 generated_title
product/update  ←── 写入标题
```

详细流程：

```
1. driver.py: _taobao_get("/product/list") — 获取在售商品 num_iid 列表
2. driver.py: _taobao_get("/product/detail") × N — 逐个拉取完整属性
3. 组装结构化 JSON 发送给 SubAgent (title-generator)
4. SubAgent 生成标题 + keyword_analysis
5. **driver.py: 新旧标题对比表呈现给用户** ← 关键变更
6. **用户逐条审核：确认 / 重新生成 / 跳过**
7. 只对用户确认的商品执行 _taobao_post("/product/update")
```

## 3. 组件设计

### 3.1 数据收集层（driver.py）

新增函数 `cmd_taobao_generate_titles(shop_id, preview, platform)`：

- 调用 `product/list` 获取所有在售商品
- 逐个调用 `product/detail` 获取完整属性
- 将每件商品的 `props` 解析为结构化 JSON
- 将 JSON 列表发送给 Agent

### 3.2 SubAgent（`agents/title-generator.md`）

输入：结构化商品数据（`num_iid` + `current_title` + `attributes` + `category` + `price` + `desc_keywords`）

前置约定（在 agent 调用 prompt 中声明）：

- 输入遵循 `agents/title-generator.md` 中定义的 JSON 格式
- 输出也遵循其中定义的 JSON 输出格式
- 标题需符合淘宝 30 汉字上限，保留原有关键词

### 3.3 接口契约

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | string | 淘宝商品 ID |
| `current_title` | string | 当前商品标题 |
| `category` | string | 类目路径，如 "女鞋 > 凉鞋" |
| `attributes` | object | 属性键值对（材质/跟高/款式等） |
| `price` | number | 商品售价 |
| `supplier` | string | 供应商名称 |
| `desc_keywords` | string[] | 从 desc 字段提取的关键词 |

输出：

| 字段 | 类型 | 说明 |
|------|------|------|
| `num_iid` | string | 对应输入的商品 ID |
| `original_title` | string | 原标题（回传验证） |
| `original_keywords` | string[] | 拆解出的原有关键词 |
| `generated_title` | string | 生成的新标题 |
| `keywords_preserved` | boolean | 原关键词是否全部保留 |
| `keyword_analysis` | object | 各优先级关键词使用情况 |
| `length` | int | 标题汉字数 |
| `quality_score` | int | 0-100 质量分 |

## 4. 输出 Schema

SubAgent 调用时通过 `schema` 参数强约束输出格式，确保结构验证在 Agent 侧完成：

```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "num_iid": { "type": "string" },
          "original_title": { "type": "string" },
          "original_keywords": { "type": "array", "items": { "type": "string" } },
          "generated_title": { "type": "string" },
          "keywords_preserved": { "type": "boolean" },
          "length": { "type": "integer" },
          "quality_score": { "type": "integer", "minimum": 0, "maximum": 100 }
        },
        "required": ["num_iid", "generated_title", "keywords_preserved", "quality_score"]
      }
    }
  },
  "required": ["results"]
}
```

## 5. 用户确认流程

生成完成后不直接写入，先展示对比表：

```
编号 | 原标题              | 新标题                              | 分数 | 操作
─────┼────────────────────┼─────────────────────────────────────┼──────┼──────
1    | 厚底                | 2026夏季厚底松糕凉鞋女百搭            | 85   | [✓] [↻] [✗]
2    | 一字式扣带,高跟鞋     | 2026夏季真皮高跟凉鞋女一字扣带百搭     | 90   | [✓] [↻] [✗]
3    | 魔术贴              | 2026夏季魔术贴平底凉鞋女休闲           | 88   | [✓] [↻] [✗]
```

- **✓ 确认** — 写入淘宝，执行 `product/update`
- **↻ 重新生成** — 调整参数后重新跑 SubAgent
- **✗ 跳过** — 维持原标题不变

## 6. 错误处理

| 场景 | 处理 |
|------|------|
| `product/detail` 调用失败 | 跳过该商品，记录 num_iid 到错误列表 |
| SubAgent 超时/无响应 | 重试 1 次，仍失败则跳过并报告 |
| `keywords_preserved: false` | 打印警告，允许写入但标记为"需人工审核" |
| `quality_score < 70` | 预览模式下降分标题高亮显示 |
| `product/update` 失败 | 记录错误，继续处理下一件 |

## 7. 测试计划

1. 单元测试（`test_driver.py`）
   - 属性解析：`材质=皮` → `真皮`
   - 关键词拆解：`"一字式扣带,高跟鞋"` → `["一字式扣带", "高跟鞋"]`
   - 价格段映射：38 → "百搭/舒适"
2. 集成测试
   - 真实店铺跑一批商品，验证 SubAgent 返回符合 Schema
   - 确认流程：模拟用户全部确认 / 部分跳过
3. 质量检查
   - 抽查 20 个生成标题校验长度/重复词/违禁词
   - 用生成标题在淘宝搜索验证匹配率

## 8. 部署依赖

- `product/detail` 接口已打通（taobao_item_get gateway）
- `product/update` 接口已打通（taobao_item_update_title gateway）
- `agents/title-generator.md` 已提交
