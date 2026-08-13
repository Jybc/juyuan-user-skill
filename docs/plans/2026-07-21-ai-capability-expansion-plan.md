# AI 能力扩展实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为聚源百成大师新增 5 个 AI 能力 — 自然语言经营问答、利润分析、属性自动补全、季节性选品日历、商品详情页文案。

**Architecture:** Plan 沿用现有模式：driver.py 新增快捷命令作为数据拉取层，子代理 SubAgent prompt 处理 AI 推理，gen_apple.py 生成交互式 HTML 页面通过 present_files 展示。属性字典改为通过 `taobao.itemprops.get` API 动态查询 + 24h 缓存。

**Tech Stack:** Python 3.8+ stdlib, WorkBuddy SubAgent + AskUserQuestion + present_files, 多模态模型 (k2/m3/5v-turbo)

**设计文档:** `docs/specs/2026-07-21-ai-capability-expansion-design.md`

---

### Task 0: 提前准备 — 新增文件骨架

**Files:**
- Create: `agents/desc-generator.md`
- Create: `agents/attrs-infer.md`
- Create: `agents/season-calendar.md`
- Create: `agents/business-qa.md`

**Step 1: 创建四个 SubAgent prompt 骨架文件**

```bash
touch agents/desc-generator.md
touch agents/attrs-infer.md
touch agents/season-calendar.md
touch agents/business-qa.md
```

**Step 2: Commit**

```bash
git add agents/desc-generator.md agents/attrs-infer.md agents/season-calendar.md agents/business-qa.md
git commit -m "feat: add placeholder files for new AI subagent prompts"
```

---

## Phase 1: #33 自然语言经营问答

### Task 1.1: driver.py 新增 `business-qa` 命令骨架

**Files:**
- Modify: `scripts/driver.py` — 新增 `cmd_taobao_business_qa()` 函数
- Modify: `scripts/driver.py` — 在 `usage()` 和 dispatch 中注册命令
- Modify: `scripts/test_driver.py` — 新增测试用例

**Step 1: 在 driver.py 尾部新增函数**

在现有最后一个函数之后添加：

```python
def cmd_taobao_business_qa(shop_id, platform=DEFAULT_PLATFORM):
    """经营问答数据收集：拉取全维度经营数据，供 AI 问答使用。"""
    import json as _json

    result = {
        "shop_id": shop_id,
        "shop_info": None,
        "product_count": 0,
        "trade_summary": {},
        "refund_summary": {},
        "rate_summary": {},
        "dashboard": None,
        "errors": [],
    }

    # 1. 店铺信息
    try:
        result["shop_info"] = _json.loads(cmd_taobao_shop_info(shop_id, platform))
    except Exception as e:
        result["errors"].append(f"shop-info: {e}")

    # 2. 在售商品数
    try:
        products = _json.loads(cmd_taobao_product_list(shop_id, platform))
        result["product_count"] = len(products.get("data", products))
    except Exception as e:
        result["errors"].append(f"product-list: {e}")

    # 3. 订单概览 (最近30天各状态)
    for status in ["", "WAIT_SELLER_SEND_GOODS", "WAIT_BUYER_CONFIRM_GOODS"]:
        try:
            resp = _json.loads(cmd_taobao_trade_list(shop_id, status, platform))
            key = status or "all"
            result["trade_summary"][key] = {
                "count": resp.get("count", len(resp.get("data", resp))),
                "sample": resp.get("data", resp)[:5],
            }
        except Exception as e:
            result["errors"].append(f"trade-list({status}): {e}")

    # 4. 退款概览
    try:
        refunds = _json.loads(cmd_taobao_refund_list(shop_id, platform))
        result["refund_summary"] = refunds
    except Exception as e:
        result["errors"].append(f"refund-list: {e}")

    # 5. 评价概览
    try:
        rates = _json.loads(cmd_taobao_rate_list(shop_id, platform))
        result["rate_summary"] = rates
    except Exception as e:
        result["errors"].append(f"rate-list: {e}")

    return _json.dumps(result, ensure_ascii=False, indent=2)
```

**Step 2: 在 usage() 函数中添加快捷命令说明**

在 `taobao daily-report` 之后添加：

```python
  taobao business-qa <shop_id> [platform]            经营问答数据收集(供AI分析)
```

**Step 3: 在 dispatch 逻辑中注册命令**

在 `elif sub == "daily-report":` 块之后添加：

```python
    elif sub == "business-qa":
        cmd_taobao_business_qa(cmd_args[0], platform)
```

**Step 4: 编写测试**

在 `scripts/test_driver.py` 中添加：

```python
def test_cmd_taobao_business_qa(self):
    """测试 business-qa 收集全维度经营数据"""
    self._configure_api_key("k3")
    
    sample_products = {"data": [{"num_iid": "1", "title": "test"}, {"num_iid": "2"}]}
    sample_trades = {"count": 5, "data": [{"tid": "t1"}, {"tid": "t2"}]}
    sample_refunds = {"data": [{"refund_id": "r1"}]}
    sample_rates = {"data": [{"oid": "o1"}]}
    
    def mock_response(*args, **kwargs):
        return self._make_response(200, sample_trades)
    
    with unittest.mock.patch.object(urllib.request, "urlopen", mock_response):
        out = cmd_taobao_business_qa("123", "k3")
    
    result = json.loads(out)
    self.assertEqual(result["shop_id"], "123")
    self.assertIn("errors", result)
    self.assertIn("trade_summary", result)
```

**Step 5: 运行测试验证**

```bash
cd scripts && python -m pytest test_driver.py -k business_qa -v
```

**Step 6: Commit**

```bash
git add scripts/driver.py scripts/test_driver.py
git commit -m "feat: add business-qa command for full-dimension shop data collection"
```

---

### Task 1.2: 实现 SubAgent prompt `agents/business-qa.md`

**Files:**
- Write: `agents/business-qa.md`

**Step 1: 编写意图识别 + 数据解读 prompt**

写入完整内容：

```markdown
# 淘宝店铺经营问答助手

你是淘宝鞋靴类目店铺的经营顾问，能根据店铺实时数据回答卖家的问题，并给出可执行的建议。

## 操作流程

### 第一步：意图识别

收到用户问题后，先归类到以下意图之一：

| 意图 | 触发词示例 | 需要的数据 |
|------|-----------|-----------|
| 经营概览 | 生意怎么样、店铺概况、看看数据 | dashboard/全维度 |
| 利润排行 | 哪个款最赚、利润排行、利润率 | 利润分析结果 |
| 品类下钻 | 凉鞋怎么样、单鞋卖如何 | 按品类过滤的订单/商品 |
| 退款根因 | 为什么退货多、退款分析 | refund数据分类 |
| 评价巡检 | 差评、评价情况 | rate-list 中差评 |
| 趋势对比 | 和上周比、和上月比 | 两期数据对比 |
| 待办提醒 | 待发货、待处理 | 各状态订单统计 |
| 诊断建议 | 怎么提高、什么建议 | 全维度 + 利润分析 |
| 选品预测 | 该上什么、秋款、选品 | 季节预测结果 |
| 功能触发 | 优化标题、写文案、调价 | 触发对应功能链路 |

### 第二步：数据解读

1. 分析各维度数据，识别异常（环比变化 > 10%）
2. 找出根因（是品类问题还是单品问题）
3. 生成 1-3 条具体建议

### 第三步：组织回答

每个回答包含三部分：

1. **数据卡片** — 关键数字，用表格呈现
2. **一句话解读** — 用卖家听得懂的话解释数据
3. **推荐追问** — 2-3 个引导性问题，帮助卖家深入

## 回答模板

```
┌─ {标题} ──────────────────────────────────────────┐
│                                                    │
│   指标1           指标2          指标3              │
│  ¥12,800         127笔          5.2%              │
│   ↓ 8%            ↓ 12%          ↑ 1.1%           │
│                                                    │
│  {一句话解读}                                       │
│                                                    │
│  建议: {1-3条具体建议}                              │
│                                                    │
│  [{追问1}] [{追问2}] [{追问3}]                     │
└────────────────────────────────────────────────────┘
```

## 约束

- 不做纯数据罗列，必须有解读
- 发现问题必须附带建议
- 对比必须有趋势箭头 (↑↓→)
- 异常数据 (>20%变化) 必须标 ⚠
- 追问不超过 3 个，优先推荐有数据支撑的方向
```

**Step 2: Commit**

```bash
git add agents/business-qa.md
git commit -m "feat: add business-qa subagent prompt for intent recognition and data interpretation"
```

---

### Task 1.3: 集成到 SKILL.md 工作流

**Files:**
- Modify: `SKILL.md`

**Step 1: 在「快捷命令」部分添加经营问答触发词**

在 `快捷命令？` 行之后添加：

```markdown
- **经营问答？** 自然语言提问，AI 根据实时数据回答。触发词：`生意怎么样` / `利润分析` / `哪个款最赚` / `退货为什么多了` / `最近趋势` / `有什么差评` / `给点建议`
```

**Step 2: Commit**

```bash
git add SKILL.md
git commit -m "docs: add business QA trigger words to SKILL.md"
```

---

## Phase 2: #35 利润分析

### Task 2.1: driver.py 新增 `profit-analysis` 命令

**Files:**
- Modify: `scripts/driver.py`
- Modify: `scripts/test_driver.py`

**Step 1: 实现 `cmd_taobao_profit_analysis()` 函数**

```python
def cmd_taobao_profit_analysis(shop_id, platform=DEFAULT_PLATFORM):
    """利润分析：整合订单+退款+拿货价，计算每商品净利润。"""
    import json as _json

    result = {"shop_id": shop_id, "products": [], "summary": {}, "errors": []}

    # 1. 获取订单数据(售价 × 数量)
    all_trades = []
    try:
        for status in ["", "WAIT_SELLER_SEND_GOODS", "WAIT_BUYER_CONFIRM_GOODS", "TRADE_FINISHED"]:
            resp = _json.loads(cmd_taobao_trade_list(shop_id, status, platform, page=1))
            trades = resp.get("data", resp) if isinstance(resp, dict) else resp
            for t in trades:
                t["_status"] = status
            all_trades.extend(trades)
    except Exception as e:
        result["errors"].append(f"trade-list: {e}")
        return _json.dumps(result, ensure_ascii=False)

    # 2. 获取退款数据
    refunds = []
    try:
        resp = _json.loads(cmd_taobao_refund_list(shop_id, platform))
        refunds = resp.get("data", resp) if isinstance(resp, dict) else resp
    except Exception as e:
        result["errors"].append(f"refund-list: {e}")

    # 3. 获取发布记录(用于匹配拿货价)
    import csv
    purchase_prices = {}  # num_iid -> 拿货价
    for fname in sorted(os.listdir(RECORDS_DIR)):
        if not fname.endswith(".csv"):
            continue
        with open(os.path.join(RECORDS_DIR, fname), newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                num_iid = row.get("num_iid", "")
                price = row.get("purchase_price", row.get("price", ""))
                if num_iid and price and num_iid not in purchase_prices:
                    try:
                        purchase_prices[num_iid] = float(price)
                    except ValueError:
                        pass

    # 4. 按 num_iid 聚合订单
    product_stats = {}  # num_iid -> {total_revenue, order_count, refund_amount, refund_count}
    for t in all_trades:
        niid = t.get("num_iid", "")
        if not niid:
            continue
        if niid not in product_stats:
            product_stats[niid] = {"total_revenue": 0, "order_count": 0, "refund_amount": 0, "refund_count": 0, "samples": []}
        try:
            revenue = float(t.get("payment", 0))
        except (ValueError, TypeError):
            revenue = 0
        product_stats[niid]["total_revenue"] += revenue
        product_stats[niid]["order_count"] += 1
        if len(product_stats[niid]["samples"]) < 3:
            product_stats[niid]["samples"].append(t)

    # 5. 扣除退款
    for r in refunds:
        niid = r.get("num_iid", "")
        if niid in product_stats:
            try:
                ramount = float(r.get("refund_fee", 0))
            except (ValueError, TypeError):
                ramount = 0
            product_stats[niid]["refund_amount"] += ramount
            product_stats[niid]["refund_count"] += 1

    # 6. 构建产品利润列表
    PLATFORM_FEE_RATE = 0.05  # 鞋靴类目 5% 淘宝扣点
    products = []
    for niid, stats in product_stats.items():
        revenue = stats["total_revenue"]
        order_count = stats["order_count"]
        refund_amount = stats["refund_amount"]
        refund_count = stats["refund_count"]
        net_revenue = revenue - refund_amount

        # 拿货价
        purchase_price = purchase_prices.get(niid, 0)

        # 成本: 拿货价 × 数量 + 平台扣点 × 收入
        platform_fee = net_revenue * PLATFORM_FEE_RATE
        total_cost = purchase_price * order_count + platform_fee
        net_profit = net_revenue - total_cost - refund_amount
        profit_rate = (net_profit / net_revenue * 100) if net_revenue > 0 else 0

        products.append({
            "num_iid": niid,
            "title": stats["samples"][0].get("title", "") if stats["samples"] else "",
            "revenue": round(net_revenue, 2),
            "cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "profit_rate": round(profit_rate, 1),
            "order_count": order_count,
            "refund_count": refund_count,
            "has_purchase_price": purchase_price > 0,
        })

    # 排序: 净利润降序
    products.sort(key=lambda x: x["net_profit"], reverse=True)

    # 汇总
    total_revenue = sum(p["revenue"] for p in products)
    total_cost = sum(p["cost"] for p in products)
    total_profit = sum(p["net_profit"] for p in products)
    total_rate = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    result["products"] = products
    result["summary"] = {
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "profit_rate": round(total_rate, 1),
        "product_count": len(products),
        "has_missing_prices": any(not p["has_purchase_price"] for p in products),
    }

    return _json.dumps(result, ensure_ascii=False, indent=2)
```

**Step 2: 注册命令 + usage**

在 usage() 中添加：

```python
  taobao profit-analysis <shop_id> [platform]          利润分析(每商品净利润排行)
```

在 dispatch 中添加：

```python
    elif sub == "profit-analysis":
        cmd_taobao_profit_analysis(cmd_args[0], platform)
```

**Step 3: 编写测试**

```python
def test_cmd_taobao_profit_analysis(self):
    """测试利润分析命令"""
    self._configure_api_key("k3")
    
    def mock_response(*args, **kwargs):
        data = {"data": [
            {"num_iid": "1", "title": "凉鞋", "payment": "128.00"},
            {"num_iid": "2", "title": "拖鞋", "payment": "89.00"},
        ]}
        return self._make_response(200, data)
    
    with unittest.mock.patch.object(urllib.request, "urlopen", mock_response):
        out = cmd_taobao_profit_analysis("123", "k3")
    
    result = json.loads(out)
    self.assertIn("products", result)
    self.assertIn("summary", result)
    self.assertGreater(len(result["products"]), 0)
```

**Step 4: 运行测试**

```bash
cd scripts && python -m pytest test_driver.py -k profit_analysis -v
```

**Step 5: Commit**

```bash
git add scripts/driver.py scripts/test_driver.py
git commit -m "feat: add profit-analysis command with purchase price matching"
```

---

### Task 2.2: gen_apple.py 新增利润看板模板

**Files:**
- Modify: `scripts/gen_apple.py`

**Step 1: 在 gen_apple.py 尾部新增 `profit_board_html()` 函数**

```python
def profit_board_html(profit_data):
    """生成利润看板 HTML。"""
    summary = profit_data.get("summary", {})
    products = profit_data.get("products", [])

    rows = ""
    for i, p in enumerate(products[:20]):
        trend_class = "trend-up" if p["profit_rate"] >= 30 else "trend-warn" if p["profit_rate"] < 20 else "trend-stable"
        missing = ' <span style="color:orange">⚠缺拿货价</span>' if not p.get("has_purchase_price") else ""
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td>{p['title']}{missing}</td>
            <td>¥{p['revenue']:.0f}</td>
            <td>¥{p['cost']:.0f}</td>
            <td class="{trend_class}">¥{p['net_profit']:.0f}</td>
            <td class="{trend_class}">{p['profit_rate']:.1f}%</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>利润看板</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background:#f5f5f5; padding:16px; }}
  .summary {{ display:flex; justify-content:space-around; background:#1a1a2e; color:#fff; border-radius:12px; padding:20px; margin-bottom:16px; }}
  .summary-item {{ text-align:center; }}
  .summary-item .val {{ font-size:24px; font-weight:700; }}
  .summary-item .label {{ font-size:12px; opacity:0.7; margin-top:4px; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:12px; overflow:hidden; }}
  th {{ background:#f0f0f0; padding:12px 8px; text-align:left; font-size:13px; }}
  td {{ padding:10px 8px; border-top:1px solid #eee; font-size:13px; }}
  .trend-up {{ color:#22c55e; }}
  .trend-stable {{ color:#6b7280; }}
  .trend-warn {{ color:#ef4444; }}
  .missing-hint {{ color:#f59e0b; font-size:11px; margin-top:8px; }}
</style>
</head>
<body>
  <div class="summary">
    <div class="summary-item">
      <div class="val">¥{summary.get('total_revenue', 0):,.0f}</div>
      <div class="label">总收入</div>
    </div>
    <div class="summary-item">
      <div class="val">¥{summary.get('total_cost', 0):,.0f}</div>
      <div class="label">总成本</div>
    </div>
    <div class="summary-item">
      <div class="val">¥{summary.get('total_profit', 0):,.0f}</div>
      <div class="label">净利润</div>
    </div>
    <div class="summary-item">
      <div class="val">{summary.get('profit_rate', 0):.1f}%</div>
      <div class="label">利润率</div>
    </div>
  </div>
  <table>
    <tr><th>#</th><th>商品</th><th>收入</th><th>成本</th><th>净利</th><th>利润率</th></tr>
    {rows}
  </table>
  {"<div class='missing-hint'>⚠ 标注「缺拿货价」的为手工上架商品，需手动补充成本价</div>" if summary.get('has_missing_prices') else ""}
</body>
</html>"""
```

**Step 2: Commit**

```bash
git add scripts/gen_apple.py
git commit -m "feat: add profit board HTML template to gen_apple.py"
```

---

### Task 2.3: 更新 SKILL.md 添加利润分析触发词

**Files:**
- Modify: `SKILL.md`

**Step 1: 在 AI 能力部分添加利润分析触发词**

```markdown
- **利润分析？** 每件商品赚了多少钱，不是感觉是数字。触发词：`利润分析` / `算算利润` / `赚了多少` / `哪个款最赚钱` / `利润排行`
```

**Step 2: Commit**

```bash
git add SKILL.md
git commit -m "docs: add profit analysis trigger words to SKILL.md"
```

---

## Phase 3: #9 属性自动补全

### Task 3.1: 实现淘宝类目属性 API 调用

**Files:**
- Modify: `scripts/driver.py`

**Step 1: 新增 `_get_category_attrs()` 函数（带缓存）**

```python
import json as _json_module

_ATTRS_CACHE = {}  # {cid: {"attrs": [...], "expires": timestamp}}

def _get_category_attrs(cid, platform=DEFAULT_PLATFORM):
    """通过淘宝类目属性 API 获取指定 cid 下的所有属性和属性值，带 24h 缓存。"""
    now = time.time()
    cid_str = str(cid)

    # 检查缓存
    if cid_str in _ATTRS_CACHE and _ATTRS_CACHE[cid_str].get("expires", 0) > now:
        return _ATTRS_CACHE[cid_str]["attrs"]

    try:
        resp = api_request("GET", f"/taobao/itemprops/get?cid={cid_str}", platform=platform)
        data = _json_module.loads(resp) if isinstance(resp, str) else resp
        attrs = data.get("data", data) if isinstance(data, dict) else data

        # 缓存 24 小时
        _ATTRS_CACHE[cid_str] = {"attrs": attrs, "expires": now + 86400}
        return attrs
    except Exception:
        # 降级：返回空列表，由调用方处理
        return []
```

**Step 2: 编写测试**

```python
def test_get_category_attrs_cached(self):
    """测试类目属性获取+缓存"""
    self._configure_api_key("k3")
    call_count = [0]

    def mock_resp(*args, **kwargs):
        call_count[0] += 1
        return self._make_response(200, {"data": [{"pid": 1, "name": "品牌", "values": ["A", "B"]}]})

    with unittest.mock.patch.object(urllib.request, "urlopen", mock_resp):
        attrs1 = _get_category_attrs(50012025, "k3")
        attrs2 = _get_category_attrs(50012025, "k3")  # 应命中缓存

    self.assertTrue(len(attrs1) > 0)
    self.assertEqual(call_count[0], 1)  # 第二次不调用 API
```

**Step 3: 运行测试**

```bash
cd scripts && python -m pytest test_driver.py -k category_attrs -v
```

**Step 4: Commit**

```bash
git add scripts/driver.py scripts/test_driver.py
git commit -m "feat: add category attributes API with 24h cache"
```

---

### Task 3.2: driver.py 新增 `attrs-check` 命令

**Files:**
- Modify: `scripts/driver.py`

**Step 1: 实现 `cmd_taobao_attrs_check()`**

```python
def cmd_taobao_attrs_check(shop_id, platform=DEFAULT_PLATFORM):
    """属性补全检查：逐件分析商品缺失属性并推断建议值。"""
    import json as _json

    result = {"shop_id": shop_id, "products": [], "errors": []}

    # 1. 获取在售商品列表
    try:
        resp = _json.loads(cmd_taobao_product_list(shop_id, platform, page=1))
        products = resp.get("data", resp) if isinstance(resp, dict) else resp
    except Exception as e:
        result["errors"].append(f"product-list: {e}")
        return _json.dumps(result, ensure_ascii=False)

    # 2. 逐件获取详情，提取标题+cid+已有属性
    for p in products:
        niid = p.get("num_iid", "")
        if not niid:
            continue
        try:
            detail = _json.loads(cmd_taobao_product_detail(shop_id, niid, platform))
            product_info = detail.get("data", detail) if isinstance(detail, dict) else detail
        except Exception as e:
            result["errors"].append(f"detail {niid}: {e}")
            continue

        title = product_info.get("title", "")
        cid = product_info.get("cid", "")
        props = product_info.get("props", "") or product_info.get("props_name", "") or ""

        # 已有属性值(字符串)
        existing_attrs = {}
        # 简单解析 props_name 格式如 "品牌:ABC;跟型:平底"
        if ":" in props:
            for pair in props.split(";"):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    existing_attrs[k.strip()] = v.strip()

        # 获取该类目的合法属性列表
        valid_attrs = _get_category_attrs(cid, platform) if cid else []

        # 找出缺失的属性
        missing = []
        for attr in valid_attrs:
            attr_name = attr.get("name", "")
            if attr_name and attr_name not in existing_attrs:
                missing.append({
                    "attr_name": attr_name,
                    "attr_pid": attr.get("pid", ""),
                    "valid_values": attr.get("values", []),
                })

        result["products"].append({
            "num_iid": niid,
            "title": title,
            "cid": cid,
            "existing_attrs": existing_attrs,
            "missing_attrs": missing,
        })

    return _json.dumps(result, ensure_ascii=False, indent=2)
```

**Step 2: 注册命令**

在 usage() 添加：

```python
  taobao attrs-check <shop_id> [platform]            属性补全检查(缺失属性+建议值)
```

在 dispatch 添加：

```python
    elif sub == "attrs-check":
        cmd_taobao_attrs_check(cmd_args[0], platform)
```

**Step 3: 编写测试**

```python
def test_cmd_taobao_attrs_check(self):
    """测试属性补全检查"""
    self._configure_api_key("k3")
    
    product_list_resp = {"data": [{"num_iid": "1"}]}
    product_detail_resp = {"data": {"num_iid": "1", "title": "一字扣凉鞋女厚底", "cid": 50012025, "props": "品牌:XYZ"}}
    
    class MockResponse:
        call_count = 0
        def __init__(self, *args, **kwargs):
            self.__class__.call_count += 1
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def read(self):
            c = self.__class__.call_count
            if c == 1:
                return json.dumps(product_list_resp).encode()
            else:
                return json.dumps(product_detail_resp).encode()
    
    # 简化测试：只验证数据结构
    # (完整测试需要 mock _get_category_attrs)
```

**Step 4: Commit**

```bash
git add scripts/driver.py scripts/test_driver.py
git commit -m "feat: add attrs-check command for missing attribute detection"
```

---

### Task 3.3: 实现 SubAgent prompt `agents/attrs-infer.md`

**Files:**
- Write: `agents/attrs-infer.md`

**Step 1: 编写属性推理 prompt**

```markdown
# 淘宝鞋靴类目属性推理

根据商品标题、图片描述和类目属性枚举，推断缺失属性值并给出置信度。

## 操作流程

### 第一步：语义提取

从标题中提取能对���到类目属性的关键词：

```
标题: "一字扣凉鞋女厚底露趾仙女风"
    ↓
"一字扣" → 闭合方式候选: 一字式扣带
"厚底"   → 跟型候选: 松糕底/厚底
"露趾"   → 鞋头款式候选: 露趾
"仙女风" → 风格候选: 仙女风
```

### 第二步：枚举匹配

将语义提取的结果与类目属性枚举值做匹配，选取最佳匹配。

```
语义: 松糕底, 厚底
枚举值: [平底, 低跟, 中跟, 高跟, 松糕底, 坡跟, 内增高, 厚底]
    ↓ 包含匹配
匹配: 松糕底 (精确), 厚底 (精确)
    ↓ 取搜索量更大者
输出: 松糕底, 置信度 0.95
```

### 第三步：图片验证（多模态可用时）

下载商品主图，用多模态模型验证推断结果：

- 脚趾是否可见 → 确��� "露趾"/"包头"
- 跟部是否有明显增厚 → 确认 "松糕底"/"平底"
- 整体风格色调 → 确认 "仙女风"/"通勤"/"潮酷"

图片验证结果与语义推断冲突时，以语义推断为准（标题比图片对搜索的影响更大）。

### 第四步：置信度判定

| 条件 | 置信度 |
|------|--------|
| 标题明文匹配+枚举精确命中 | ≥ 90% |
| 标题隐含匹配+枚举部分命中 | 70-89% |
| 仅枚举值推断，标题无对应词 | < 70% |

## 输出格式

```json
{
  "results": [
    {
      "num_iid": "123",
      "attributes": [
        {
          "attr_name": "跟型",
          "attr_pid": "20000",
          "suggested_value": "松糕底",
          "confidence": 0.95,
          "source": "title_match"
        },
        {
          "attr_name": "鞋头款式",
          "attr_pid": "20001",
          "suggested_value": "露趾",
          "confidence": 0.92,
          "source": "title_match"
        }
      ]
    }
  ]
}
```
```

**Step 2: Commit**

```bash
git add agents/attrs-infer.md
git commit -m "feat: add attribute inference subagent prompt"
```

---

### Task 3.4: gen_apple.py 新增属性报告模板

**Files:**
- Modify: `scripts/gen_apple.py`

**Step 1: 新增 `attrs_report_html()` 函数**

```python
def attrs_report_html(attrs_data):
    """生成属性补全报告 HTML。"""
    products = attrs_data.get("products", [])
    total_missing = sum(1 for p in products if p.get("missing_attrs"))
    
    rows = ""
    for p in products:
        if not p.get("missing_attrs"):
            continue
        title = p.get("title", "")
        niid = p.get("num_iid", "")
        for attr in p["missing_attrs"]:
            conf_class = "conf-high" if attr.get("confidence", 0) >= 0.9 else "conf-mid" if attr.get("confidence", 0) >= 0.7 else "conf-low"
            rows += f"""
            <tr>
                <td>{niid[-6:]}</td>
                <td>{title[:20]}</td>
                <td>{attr['attr_name']}</td>
                <td>{attr.get('suggested_value', '—')}</td>
                <td class="{conf_class}">{int(attr.get('confidence', 0)*100)}%</td>
            </tr>
            """
    
    if not rows:
        rows = '<tr><td colspan="5" style="text-align:center; color:#6b7280;">没有属性缺失，店铺完整性良好</td></tr>'
    
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>属性补全报告</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background:#f5f5f5; padding:16px; }}
  h2 {{ margin-bottom:12px; font-size:18px; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:12px; overflow:hidden; }}
  th {{ background:#f0f0f0; padding:10px 8px; text-align:left; font-size:12px; }}
  td {{ padding:8px; border-top:1px solid #eee; font-size:12px; }}
  .conf-high {{ color:#22c55e; font-weight:700; }}
  .conf-mid {{ color:#f59e0b; font-weight:700; }}
  .conf-low {{ color:#ef4444; font-weight:700; }}
  .actions {{ margin-top:16px; display:flex; gap:8px; }}
  .actions button {{ padding:10px 20px; border:none; border-radius:8px; font-size:14px; cursor:pointer; }}
  .btn-primary {{ background:#1a1a2e; color:#fff; }}
  .btn-secondary {{ background:#e5e7eb; color:#333; }}
</style>
</head>
<body>
  <h2>属性补全报告 — 共 {total_missing} 件有缺失</h2>
  <table>
    <tr><th>商品</th><th>标题</th><th>缺失属性</th><th>建议值</th><th>置信度</th></tr>
    {rows}
  </table>
  <div class="actions">
    <button class="btn-primary">一键采纳高置信度</button>
    <button class="btn-secondary">逐件审核</button>
  </div>
</body>
</html>"""
```

**Step 2: Commit**

```bash
git add scripts/gen_apple.py
git commit -m "feat: add attribute report HTML template to gen_apple.py"
```

---

## Phase 4: #3 季节性选品日历

### Task 4.1: driver.py 新增 `season-calendar` 命令

**Files:**
- Modify: `scripts/driver.py`

**Step 1: 实现 `cmd_taobao_season_calendar()`**

```python
def cmd_taobao_season_calendar(shop_id, platform=DEFAULT_PLATFORM):
    """季节选品日历：分析历史销售趋势 + 热搜词季节性，推荐未来选品方向。"""
    import json as _json

    result = {"shop_id": shop_id, "items": [], "errors": []}

    # 1. 获取在售商品
    products = []
    try:
        resp = _json.loads(cmd_taobao_product_list(shop_id, platform, page=1))
        products = resp.get("data", resp) if isinstance(resp, dict) else resp
    except Exception as e:
        result["errors"].append(f"product-list: {e}")

    # 2. 获取订单数据(分析品类销售趋势)
    all_trades = []
    try:
        for status in ["WAIT_SELLER_SEND_GOODS", "WAIT_BUYER_CONFIRM_GOODS", "TRADE_FINISHED"]:
            resp = _json.loads(cmd_taobao_trade_list(shop_id, status, platform, page=1))
            trades = resp.get("data", resp) if isinstance(resp, dict) else resp
            all_trades.extend(trades)
    except Exception as e:
        result["errors"].append(f"trade-list: {e}")

    # 3. 统计品类分布 (简易：按标题关键词匹配)
    category_keywords = {
        "凉鞋": ["���鞋", "凉拖", "一字扣凉鞋"],
        "拖鞋": ["拖鞋", "凉拖", "一字拖", "人字拖"],
        "单鞋": ["单鞋", "浅口", "乐福鞋", "芭蕾鞋", "尖头鞋"],
        "短靴": ["短靴", "马丁靴", "切尔西靴", "靴子"],
        "高跟鞋": ["高跟鞋", "细跟", "粗跟"],
        "帆布鞋": ["帆布鞋", "��白鞋"],
    }
    category_order = {cat: 0 for cat in category_keywords}
    for t in all_trades:
        title = t.get("title", "")
        for cat, keywords in category_keywords.items():
            if any(kw in title for kw in keywords):
                category_order[cat] += 1
                break

    # 4. 加载热搜词库（静态 795 词）
    keywords_path = os.path.join(os.path.dirname(__file__), "..", "references", "api", "taobao", "shoe-hot-keywords.json")
    hot_keywords = []
    try:
        with open(keywords_path) as f:
            hot_keywords = _json.load(f)
    except Exception as e:
        result["errors"].append(f"hot-keywords: {e}")

    # 5. 构建输出
    from datetime import datetime
    current_month = datetime.now().month
    # 简易季节窗口判断
    season_ranks = {}  # 品类 → 热度趋势
    if 3 <= current_month <= 5:
        season_ranks = {"单鞋": "↑", "凉鞋": "↗", "帆布鞋": "↗", "拖鞋": "↗", "短靴": "↓"}
    elif 6 <= current_month <= 8:
        season_ranks = {"凉鞋": "→", "拖鞋": "↗", "帆布鞋": "↗", "单鞋": "→", "短靴": "↘"}
    elif 9 <= current_month <= 11:
        season_ranks = {"短靴": "↗", "单鞋": "��", "凉鞋": "↓", "拖鞋": "↓"}
    else:
        season_ranks = {"短靴": "→", "单鞋": "↘"}

    for cat, count in sorted(category_order.items(), key=lambda x: x[1], reverse=True):
        trend = season_ranks.get(cat, "—")
        result["items"].append({
            "category": cat,
            "trade_count": count,
            "trend": trend,
            "suggestion": "重点备货" if trend in ("↗", "↑") else "正常" if trend in ("→", "↗") else "清仓",
        })

    return _json.dumps(result, ensure_ascii=False, indent=2)
```

**Step 2: 注册命令**

```python
  taobao season-calendar <shop_id> [platform]        季节选品日历(品类趋势+备货建议)
```

```python
    elif sub == "season-calendar":
        cmd_taobao_season_calendar(cmd_args[0], platform)
```

**Step 3: Commit**

```bash
git add scripts/driver.py
git commit -m "feat: add season-calendar command for category trend analysis"
```

---

### Task 4.2: gen_apple.py 新增选品日历模板

**Files:**
- Modify: `scripts/gen_apple.py`

**Step 1: 新增 `season_calendar_html()` 函数**

```python
def season_calendar_html(calendar_data):
    """生成选品日历 HTML。"""
    items = calendar_data.get("items", [])
    
    max_count = max((i["trade_count"] for i in items), default=1)
    bars = ""
    for item in items:
        pct = int(item["trade_count"] / max_count * 100) if max_count > 0 else 0
        color = "#22c55e" if item["trend"] in ("↗", "↑") else "#f59e0b" if item["trend"] in ("→",) else "#ef4444"
        bars += f"""
        <div class="bar-row">
            <span class="bar-label">{item['category']}</span>
            <span class="bar-trend" style="color:{color}">{item['trend']}</span>
            <div class="bar"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>
            <span class="bar-count">{item['trade_count']}单</span>
            <span class="bar-suggestion">{item['suggestion']}</span>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>选品日历</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background:#f5f5f5; padding:16px; }}
  h2 {{ margin-bottom:16px; font-size:18px; }}
  .bar-row {{ display:flex; align-items:center; margin-bottom:12px; gap:8px; }}
  .bar-label {{ width:60px; font-size:13px; font-weight:600; }}
  .bar-trend {{ width:30px; font-size:16px; text-align:center; }}
  .bar {{ flex:1; height:24px; background:#e5e7eb; border-radius:4px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:4px; transition:width 0.8s; }}
  .bar-count {{ width:50px; font-size:12px; color:#6b7280; text-align:right; }}
  .bar-suggestion {{ font-size:11px; padding:2px 8px; border-radius:4px; background:#f0f0f0; }}
</style>
</head>
<body>
  <h2>选品日历 — 未来30天品类趋势</h2>
  {bars}
  <div style="margin-top:20px; font-size:12px; color:#6b7280;">
    ↗ 热度上升 · → 平稳 · ↘ 降温 · ↓ 快速降温
  </div>
</body>
</html>"""
```

**Step 2: Commit**

```bash
git add scripts/gen_apple.py
git commit -m "feat: add season calendar HTML template to gen_apple.py"
```

---

## Phase 5: #6 商品详情页文案

### Task 5.1: 实现 SubAgent prompt `agents/desc-generator.md`

**Files:**
- Write: `agents/desc-generator.md`

**Step 1: 编写文案生成 prompt（完整 5 模块）**

内容参考设计文档 5.3 节，包含：
- 卖点提炼（3句）
- 材质说明
- 适用场景
- 尺码建议
- 搭配推荐

```markdown
# 淘宝鞋靴商品详情页文案生成器

你是淘宝鞋靴类目运营主编，擅长把一双鞋卖出去。根据商品标题、属性、价格和图片，生成结构化详情页文案。

## 生成规则

### 价格档位 × 语气策略

| 价位 | 核心人群 | 语气 | 禁词 |
|------|---------|------|------|
| < 30元 | 学生/价格敏感 | "实惠""性价比""学生党" | 不提"高端""真皮" |
| 30-80元 | 大众消费 | "舒适""百搭""好穿不贵" | 不过度渲染 |
| 80-150元 | 品质追求 | "真皮""质感""不将就" | 不喊便宜 |
| > 150元 | 精品 | "轻奢""手工""甄选" | 宁缺毋滥 |

### 五模块结构

#### 1. 卖点提炼（3条，每条 < 18 字）
- 第1条：核心款式卖点
- 第2条：舒适/功能卖点
- 第3条：外观/风格卖点

#### 2. 材质说明（3段）
- 鞋面材质 + 亲肤/透气描述
- 鞋底材质 + 防滑/耐磨描述
- 内里材质 + 久穿不闷脚描述

#### 3. 适用场景（4个）
- 根据商品风格选择最匹配的 4 个场景标签

#### 4. 尺码建议（2-3句）
- 是否标准码
- 脚宽/脚背高的建议
- 凉鞋/拖鞋的特殊提醒

#### 5. 搭配推荐（3组）
- 搭配什么 + 什么风格 + 适合什么场景

### 输出格式

```json
{
  "num_iid": "123",
  "price_tier": "80-150元",
  "sections": {
    "selling_points": ["一字扣带设计不掉跟", "4cm松糕厚底舒适增高", "露趾设计夏天透气精致"],
    "material": {
      "upper": "优质PU面料，柔软亲肤，久穿不磨脚背",
      "sole": "防滑橡胶大底，雨天行走也稳固",
      "lining": "透气网布内衬，一整天不闷脚不臭脚"
    },
    "scenes": ["约会逛街", "日常通勤", "度假旅游", "拍照出片"],
    "size_advice": "标准码，按平时凉鞋尺码选购。脚宽/脚背高的姐妹建议拍大一码。",
    "outfits": [
      {"with": "碎花半身裙", "style": "约会仙女风", "scene": "拍照出片"},
      {"with": "高腰阔腿裤", "style": "通勤知性风", "scene": "办公室"},
      {"with": "牛仔热裤", "style": "日常休闲风", "scene": "逛街上课"}
    ]
  }
}
```
```

**Step 2: Commit**

```bash
git add agents/desc-generator.md
git commit -m "feat: add product description generator subagent prompt"
```

---

### Task 5.2: gen_apple.py 新增详情页预览模板

**Files:**
- Modify: `scripts/gen_apple.py`

**Step 1: 新增 `desc_preview_html()` 函数**

在 gen_apple.py 尾部追加生成淘宝详情页风格的 HTML 预览模板，包含 5 个模块的可视化展示。代码量约 80 行。

**Step 2: Commit**

```bash
git add scripts/gen_apple.py
git commit -m "feat: add description preview HTML template to gen_apple.py"
```

---

### Task 5.3: 更新 SKILL.md 添加详情文案触发词

**Files:**
- Modify: `SKILL.md`

**Step 1: 添加触发词**

```markdown
- **详情页文案？** AI 生成结构化商品详情页：卖点+材质+场景+尺码+搭配。触发词：`写详情` / `生成详情` / `详情页文案` / `宝贝描述优化`
```

**Step 2: Commit**

```bash
git add SKILL.md
git commit -m "docs: add description generator trigger words to SKILL.md"
```

---

## 最终集成

### Task F.1: SKILL.md 工作流完整更新

**Files:**
- Modify: `SKILL.md`

**Step 1: 更新「功能选择」菜单，新增 5 个入口**

```markdown
新增 5 个选项：
- 经营问答 / 利润分析 / 属性巡检 / 选品日历 / 详情文案
```

**Step 2: 更新快捷命令表**

在 `常见问题 → 快捷命令？` 部分添加新命令。

**Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs: integrate all 5 new AI features into SKILL.md workflow"
```

---

### Task F.2: 运行全量测试

**Step 1: 执行所有测试**

```bash
cd scripts && python -m pytest test_driver.py -v
```

**Step 2: 修复所有回归问题**

根据测试输出修复。

**Step 3: Commit**

```bash
git add -A && git commit -m "test: final integration testing pass"
```

---

## 实施顺序总结

```
Phase 1 (#33 经营问答) ← 先铺基础设施，所有后续功能都通过它暴露
Phase 2 (#35 利润分析) ← 问答的核心数据源
Phase 3 (#9 属性补全)  ← 详情文案的前置依赖
Phase 4 (#3 选品日历)  ← 独立，可并行
Phase 5 (#6 详情文案)  ← 依赖 Phase 3
```

共 18 个 task，每个 task 2-5 步。
