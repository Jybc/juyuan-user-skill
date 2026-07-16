#!/usr/bin/env python3
"""K3 极速发布平台 API 驱动。纯 stdlib，无需 pip install，跨平台可用。"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

BASE_URL = "http://open.jybc.com.cn/agent"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "k3-publish")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config")
RECORDS_DIR = os.path.join(CONFIG_DIR, "records")
DEFAULT_PLATFORM = "k3"
USER_AGENT = f"juyuan-skill/1.0 (Python {sys.version_info.major}.{sys.version_info.minor})"

PLATFORMS = {"k3": "开山网", "bao66": "包牛牛"}

# ── helpers ──────────────────────────────────────────────

def ensure_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(RECORDS_DIR, exist_ok=True)


def load_all_keys():
    """读取所有已配置的 key，返回 dict。"""
    keys = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.startswith("API_KEY") and v:
                        keys[k] = v
    return keys


def load_api_key(platform=None):
    """按平台读取 API Key。
    优先读 API_KEY_{platform}= ，不存在则回退到 API_KEY= （向后兼容旧格式）。
    """
    keys = load_all_keys()
    if platform:
        key = keys.get(f"API_KEY_{platform}")
        if key:
            return key
    return keys.get("API_KEY")  # 兜底


def save_api_key(key, platform=None):
    """保存 API Key。platform 为 None 时写通用 key，否则写平台专属 key。"""
    ensure_dirs()
    keys = load_all_keys()

    if platform:
        keys[f"API_KEY_{platform}"] = key
    else:
        # 通用 key 清除所有平台专属 key
        keys = {k: v for k, v in keys.items() if not k.startswith("API_KEY_")}
        keys["API_KEY"] = key

    with open(CONFIG_FILE, "w") as f:
        for k, v in keys.items():
            f.write(f"{k}={v}\n")


def prompt_api_key(platform=None):
    """交互式输入 API Key。"""
    label = f" ({PLATFORMS.get(platform, platform)})" if platform else ""
    while True:
        print(f">>> 请提供 API-Key{label} (X-API-Key):")
        key = sys.stdin.readline().strip()
        if key:
            save_api_key(key, platform)
            print(f">>> API-Key 已保存到 {CONFIG_FILE}")
            return key
        print(">>> API-Key 不能为空，请重新输入")


def get_api_key(platform=None):
    """获取指定平台的 API Key，不存在则提示输入。"""
    key = load_api_key(platform)
    if not key:
        key = prompt_api_key(platform)
    return key


def api_request(method, path, data=None, platform=None, retries=3):
    """发送 API 请求，自动重试以应对网络波动。"""
    api_key = get_api_key(platform)
    sep = "&" if "?" in path else "?"
    url = f"{BASE_URL}{path}{sep}api_key={api_key}"
    headers = {"User-Agent": USER_AGENT}

    last_error = None
    for attempt in range(retries):
        try:
            if data:
                encoded = urllib.parse.urlencode(data).encode()
                req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
            else:
                req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode()
                # 检测可重试的服务端错误
                if resp.status in (502, 503, 504) and attempt < retries - 1:
                    time.sleep(1 * (2 ** attempt))
                    continue
                return body, resp.status
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code in (502, 503, 504) and attempt < retries - 1:
                time.sleep(1 * (2 ** attempt))
                continue
            return body, e.code
        except urllib.error.URLError as e:
            last_error = str(e.reason)
            if attempt < retries - 1:
                time.sleep(1 * (2 ** attempt))
            else:
                return f'{{"error": "{last_error}", "retries": {retries}}}', 0
    return f'{{"error": "{last_error}", "retries": {retries}}}', 0


def pretty_print(body):
    try:
        parsed = json.loads(body)
        # 友好错误提示
        if isinstance(parsed, dict) and parsed.get("code", 0) != 0:
            msg = parsed.get("msg", "")
            # 搜索字符限制提示
            if "请输入至少三个字符" in str(msg):
                parsed["_hint"] = "搜索关键词至少需要 3 个字符，已自动补全"
            # 店铺权限提示
            elif "店铺不存在或没有权限" in str(msg):
                parsed["_hint"] = "请确认 shop_id 正确，店铺是否已授权"
            # 参数缺失提示
            elif "请提供" in str(msg):
                parsed["_hint"] = f"缺少必要参数，请参考: python scripts/driver.py --help"
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except (json.JSONDecodeError, ValueError):
        print(body)


def _safe_search_keyword(keyword):
    """搜索关键词不足 3 个字符时自动补全"""
    kw = keyword.strip()
    if len(kw) < 3:
        # 尝试加空格补充长度
        padded = kw + "  "[:3 - len(kw)]
        return padded
    return kw


def _add_platform(path, platform=None):
    """给 URL path 追加 platform 参数（默认 k3）。"""
    p = platform or DEFAULT_PLATFORM
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}platform={p}"


# ── commands ─────────────────────────────────────────────

def cmd_setup():
    """设置各平台 API-Key"""
    keys = load_all_keys()

    for pid, pname in PLATFORMS.items():
        current = keys.get(f"API_KEY_{pid}", keys.get("API_KEY", "")) or "(未设置)"
        print(f"\n=== {pname} (platform={pid}) ===")
        print(f"当前 Key: {current[:20]}..." if len(current) > 20 else f"当前 Key: {current}")
        print("输入新 Key 以更新，直接回车跳过:")
        new_key = sys.stdin.readline().strip()
        if new_key:
            save_api_key(new_key, pid)
            print(f">>> {pname} API-Key 已更新")

    print("\n=== 当前配置 ===")
    cmd_show_keys()


def cmd_show_keys():
    """显示当前已配置的 API Key（脱敏）。"""
    keys = load_all_keys()
    if not keys:
        print("  (无)")
        return
    for k, v in keys.items():
        masked = v[:10] + "..." if len(v) > 10 else v
        print(f"  {k}={masked}")


def cmd_today(page="1", platform=None):
    """获取今日新款列表"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 今日新款列表 (platform={p}, page={page}) ===")
    path = _add_platform(f"/product/today?page={page}", platform)
    body, code = api_request("GET", path, platform=p)
    pretty_print(body)


def cmd_search(keyword, platform=None):
    """搜索产品"""
    import re
    kw = keyword.strip()
    # 1. 去除 HTML/XML 标签
    kw = re.sub(r'<[^>]*>', '', kw)
    # 2. 去除控制字符和不可见字符（保留常见中英文标点）
    kw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', kw)
    # 3. 长度检查：2~20 字符
    if len(kw) < 2:
        print(json.dumps({"code": 1, "msg": f"搜索关键词过短（当前{len(kw)}字），请至少输入 2 个字符", "hint": "搜索词限制 2~20 字符"}, ensure_ascii=False))
        return
    if len(kw) > 20:
        kw = kw[:20]
        print(f"[提示] 关键词已自动截断为前 20 个字符: {kw}")
    p = platform or DEFAULT_PLATFORM
    print(f"=== 搜索产品: {kw} (platform={p}) ===")
    encoded = urllib.parse.quote(kw)
    path = _add_platform(f"/product/search?wd={encoded}", platform)
    body, code = api_request("GET", path, platform=p)
    pretty_print(body)


def cmd_shops(platform=None):
    """获取已绑定店铺列表"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 店铺列表 (platform={p}) ===")
    path = _add_platform("/user/taobao-shops", platform)
    body, code = api_request("GET", path, platform=p)
    pretty_print(body)


def cmd_publish(product_ids, shop_id, shop_type, platform=None):
    """提交极速发布并自动保存记录"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 提交极速发布 (platform={p}, products={product_ids}, shop_id={shop_id}, shop_type={shop_type}) ===")

    body, code = api_request("POST", "/product/fast-publish",
                             data={
                                 "platform": p,
                                 "product_id": product_ids,
                                 "shop_id": shop_id,
                                 "shop_type": shop_type,
                             },
                             platform=p)
    pretty_print(body)

    # 解析 job-id
    job_id = "unknown"
    try:
        resp = json.loads(body)
        job_id = str(resp.get("job-id", resp.get("job_id", "unknown")))
    except (json.JSONDecodeError, ValueError):
        pass

    # 保存记录
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    record_file = os.path.join(RECORDS_DIR, f"{today}.json")

    entry = {
        "time": timestamp,
        "platform": p,
        "product_ids": product_ids,
        "shop_id": shop_id,
        "shop_type": shop_type,
        "job_id": job_id,
        "response": body,
    }

    if os.path.exists(record_file):
        with open(record_file, "r") as f:
            data = json.load(f)
        data["tasks"].append(entry)
    else:
        data = {"date": today, "tasks": [entry]}

    ensure_dirs()
    with open(record_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f">>> 发布记录已保存到 {record_file}")


def cmd_jobs(product_id, shop_id, shop_type, platform=None):
    """查看发布任务结果"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 发布任务结果 (platform={p}, product_id={product_id}, shop_id={shop_id}, shop_type={shop_type}) ===")
    params = urllib.parse.urlencode({
        "platform": p,
        "product_id": product_id,
        "shop_id": shop_id,
        "shop_type": shop_type,
    })
    path = f"/product/fast-publish-result?{params}"
    body, code = api_request("GET", path, platform=p)
    pretty_print(body)


def cmd_records(date=None):
    """查看某天的发布记录"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    record_file = os.path.join(RECORDS_DIR, f"{date}.json")
    if os.path.exists(record_file):
        with open(record_file) as f:
            print(f.read())
    else:
        print(f">>> 没有 {date} 的发布记录")


def cmd_record_list():
    """列出所有记录"""
    print("=== 已保存的发布记录 ===")
    if os.path.exists(RECORDS_DIR):
        files = sorted(
            [f for f in os.listdir(RECORDS_DIR) if f.endswith(".json")],
            reverse=True,
        )
        if files:
            for f in files:
                print(f"  {RECORDS_DIR}/{f}")
        else:
            print(">>> 暂无记录")
    else:
        print(">>> 暂无记录")


def cmd_record_export(start_date=None, end_date=None):
    """导出发布记录摘要 (CSV 格式)"""
    if not os.path.exists(RECORDS_DIR):
        print(">>> 暂无记录")
        return

    files = sorted([f for f in os.listdir(RECORDS_DIR) if f.endswith(".json")])
    if start_date:
        files = [f for f in files if f >= f"{start_date}.json"]
    if end_date:
        files = [f for f in files if f <= f"{end_date}.json"]

    print("日期,时间,平台,产品ID,店铺ID,店铺类型,任务ID")
    for fname in files:
        with open(os.path.join(RECORDS_DIR, fname)) as f:
            data = json.load(f)
        for t in data.get("tasks", []):
            shop_id = t.get("shop_id", "")
            shop_type = t.get("shop_type", "")
            print(f"{data['date']},{t['time']},{t['platform']},{t['product_ids']},{shop_id},{shop_type},{t['job_id']}")


# ── taobao shop management ─────────────────────────────────

def _taobao_path(sub_path, shop_id, platform=None):
    """构建淘宝管理 API 路径，统一附加 shop_id 和 platform"""
    p = platform or DEFAULT_PLATFORM
    sep = "&" if "?" in sub_path else "?"
    return f"/taobao{sub_path}{sep}shop_id={shop_id}&platform={p}"


def _taobao_get(sub_path, shop_id, extra_params="", platform=None):
    """淘宝管理 GET 请求"""
    p = platform or DEFAULT_PLATFORM
    path = _taobao_path(sub_path, shop_id, p)
    if extra_params:
        path += f"&{extra_params}"
    return api_request("GET", path, platform=p)


def _taobao_post(sub_path, shop_id, data, platform=None):
    """淘宝管理 POST 请求"""
    p = platform or DEFAULT_PLATFORM
    data["shop_id"] = shop_id
    data["platform"] = p
    path = f"/taobao{sub_path}"
    return api_request("POST", path, data=data, platform=p)


def cmd_taobao_shop_info(shop_id, nick="", platform=None):
    """店铺基本信息"""
    p = platform or DEFAULT_PLATFORM
    params = f"nick={urllib.parse.quote(nick)}" if nick else ""
    body, code = _taobao_get("/shop/info", shop_id, params, p)
    pretty_print(body)


def cmd_taobao_seller_info(shop_id, platform=None):
    """卖家视角店铺信息"""
    body, code = _taobao_get("/shop/seller-info", shop_id, "", platform)
    pretty_print(body)


def cmd_taobao_user_info(shop_id, platform=None):
    """卖家用户信息"""
    body, code = _taobao_get("/shop/user-info", shop_id, "", platform)
    pretty_print(body)


def cmd_taobao_product_list(shop_id, page="1", pagesize="50", platform=None):
    """在售商品列表"""
    params = f"page={page}&pagesize={pagesize}"
    body, code = _taobao_get("/product/list", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_product_inventory(shop_id, page="1", pagesize="50", platform=None):
    """仓库中商品列表"""
    params = f"page={page}&pagesize={pagesize}"
    body, code = _taobao_get("/product/inventory", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_product_detail(shop_id, num_iid, platform=None):
    """商品详情"""
    params = f"num_iid={num_iid}"
    body, code = _taobao_get("/product/detail", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_update_price(shop_id, num_iid, price, platform=None):
    """更新商品价格"""
    body, code = _taobao_post("/product/update-price", shop_id, {
        "num_iid": num_iid,
        "price": price,
    }, platform)
    pretty_print(body)


def cmd_taobao_upshelf(shop_id, num_iid, num="100", platform=None):
    """上架商品"""
    body, code = _taobao_post("/product/upshelf", shop_id, {
        "num_iid": num_iid,
        "num": num,
    }, platform)
    pretty_print(body)


def cmd_taobao_downshelf(shop_id, num_iid, platform=None):
    """下架商品"""
    body, code = _taobao_post("/product/downshelf", shop_id, {
        "num_iid": num_iid,
    }, platform)
    pretty_print(body)


def cmd_taobao_delete(shop_id, num_iid, platform=None):
    """删除商品"""
    body, code = _taobao_post("/product/delete", shop_id, {
        "num_iid": num_iid,
    }, platform)
    pretty_print(body)


def cmd_taobao_trade_list(shop_id, status="", page="1", pagesize="40", platform=None):
    """订单列表"""
    params = f"page={page}&pagesize={pagesize}"
    if status:
        params += f"&status={urllib.parse.quote(status)}"
    body, code = _taobao_get("/trade/list", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_trade_detail(shop_id, tid, platform=None):
    """订单详情"""
    params = f"tid={tid}"
    body, code = _taobao_get("/trade/detail", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_ship(shop_id, tid, express_code, track_no, platform=None):
    """发货"""
    body, code = _taobao_post("/trade/ship", shop_id, {
        "tid": tid,
        "express_code": express_code,
        "track_no": track_no,
    }, platform)
    pretty_print(body)


def cmd_taobao_update_address(shop_id, tid, receiver_name="", receiver_mobile="",
                              receiver_state="", receiver_city="", receiver_district="",
                              receiver_address="", platform=None):
    """修改收货地址"""
    data = {"tid": tid}
    for k, v in [("receiver_name", receiver_name), ("receiver_mobile", receiver_mobile),
                 ("receiver_state", receiver_state), ("receiver_city", receiver_city),
                 ("receiver_district", receiver_district), ("receiver_address", receiver_address)]:
        if v:
            data[k] = v
    body, code = _taobao_post("/trade/update-address", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_rate_list(shop_id, rate_type="give", role="seller", result="", page="1", page_size="40", platform=None):
    """评价列表"""
    params = f"rate_type={rate_type}&role={role}&page={page}&page_size={page_size}"
    if result:
        params += f"&result={result}"
    body, code = _taobao_get("/rate/list", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_rate_reply(shop_id, oid, reply, platform=None):
    """评价解释回复"""
    body, code = _taobao_post("/rate/reply", shop_id, {
        "oid": oid,
        "reply": reply,
    }, platform)
    pretty_print(body)


def cmd_taobao_rate_add(shop_id, tid, result, content="", oid="", platform=None):
    """新增评价"""
    data = {"tid": tid, "result": result, "role": "seller"}
    if content:
        data["content"] = content
    if oid:
        data["oid"] = oid
    body, code = _taobao_post("/rate/add", shop_id, data, platform)
    pretty_print(body)


# ── taobao trade memo ──────────────────────────

def cmd_taobao_memo_add(shop_id, tid, memo, flag="0", platform=None):
    """添加交易备注"""
    body, code = _taobao_post("/trade/memo/add", shop_id, {
        "tid": tid, "memo": memo, "flag": flag
    }, platform)
    pretty_print(body)


def cmd_taobao_memo_update(shop_id, tid, memo, flag="0", reset="false", platform=None):
    """更新交易备注"""
    data = {"tid": tid, "memo": memo, "flag": flag, "reset": reset}
    body, code = _taobao_post("/trade/memo/update", shop_id, data, platform)
    pretty_print(body)


# ── taobao oaid merge ──────────────────────────

def cmd_taobao_oaid_merge(shop_id, merge_order_ids, platform=None):
    """OAID订单合并"""
    body, code = _taobao_post("/trade/oaid-merge", shop_id, {
        "merge_order_ids": merge_order_ids
    }, platform)
    pretty_print(body)


# ── taobao refund ──────────────────────────────

def cmd_taobao_refund_list(shop_id, status="", page="1", page_size="40", platform=None):
    """退款列表"""
    p = platform or DEFAULT_PLATFORM
    params = f"page={page}&page_size={page_size}"
    if status:
        params += f"&status={status}"
    body, code = _taobao_get("/refund/receive-list", shop_id, params, p)
    pretty_print(body)


def cmd_taobao_refund_detail(shop_id, refund_id, platform=None):
    """退款详情"""
    params = f"refund_id={refund_id}"
    body, code = _taobao_get("/refund/detail", shop_id, params, platform)
    pretty_print(body)


def cmd_taobao_refund_refuse(shop_id, refund_id, refund_version, refuse_message="", platform=None):
    """拒绝退款"""
    data = {"refund_id": refund_id, "refund_version": refund_version}
    if refuse_message:
        data["refuse_message"] = refuse_message
    body, code = _taobao_post("/refund/refuse", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_refund_agree(shop_id, code, refund_infos, message="", platform=None):
    """同意退款(批量)"""
    data = {"code": code, "refund_infos": refund_infos}
    if message:
        data["message"] = message
    body, code = _taobao_post("/refund/agree", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_returngoods_agree(shop_id, refund_id, refund_version, seller_address_id, refund_phase="onsale", platform=None):
    """同意退货"""
    data = {
        "refund_id": refund_id,
        "refund_version": refund_version,
        "refund_phase": refund_phase,
        "seller_address_id": seller_address_id,
    }
    body, code = _taobao_post("/refund/returngoods-agree", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_refund_intercept(shop_id, refund_id, refund_version, platform=None):
    """卖家发起拦截"""
    body, code = _taobao_post("/refund/intercept", shop_id, {
        "refund_id": refund_id, "refund_version": refund_version
    }, platform)
    pretty_print(body)


def cmd_taobao_deliveryintercept_feedback(shop_id, refund_id, logistic_status="", fail_reason="", platform=None):
    """物流拦截结果反馈"""
    data = {"refund_id": refund_id}
    if logistic_status:
        data["logistic_status"] = logistic_status
    if fail_reason:
        data["fail_reason"] = fail_reason
    body, code = _taobao_post("/refund/deliveryintercept-feedback", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_negotiatereturn(shop_id, refund_id, refund_version, platform=None):
    """协商退货退款"""
    data = {"refund_id": refund_id, "refund_version": refund_version}
    body, code = _taobao_post("/refund/negotiatereturn", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_update_product(shop_id, num_iid, title="", desc="", platform=None):
    """更新商品信息（标题/描述）"""
    data = {"num_iid": num_iid}
    if title: data["title"] = title
    if desc: data["desc"] = desc
    body, code = _taobao_post("/product/update", shop_id, data, platform)
    pretty_print(body)


def cmd_taobao_batch_title(shop_id, mode, value, preview=True, platform=None):
    """批量优化标题 — product/list → 修改标题 → 批量更新
    mode: prefix/suffix/replace/preview
    for replace: value = 'old|new' """
    p = platform or DEFAULT_PLATFORM
    print(f"=== 批量标题优化 (shop_id={shop_id}, {p}) mode={mode} ===\n")

    body, _ = _taobao_get("/product/list", shop_id, "page=1&pagesize=50", p)
    products = json.loads(body)
    items = products.get("data", {}).get("data", {}).get("items", {}).get("item", [])
    if not items:
        print("���在售商品")
        return
    print(f"找到 {len(items)} 个商品\n")

    for i, item in enumerate(items):
        ni = item.get("num_iid", "")
        old_title = item.get("title", "")
        if mode == "prefix":
            new_title = f"{value}{old_title}"
        elif mode == "suffix":
            new_title = f"{old_title}{value}"
        elif mode == "replace":
            parts = value.split("|", 1)
            old_w, new_w = parts[0], (parts[1] if len(parts) > 1 else "")
            new_title = old_title.replace(old_w, new_w)
        else:
            new_title = old_title

        new_title = new_title[:60]  # 淘宝标题最长30个汉字
        print(f"[{i+1}/{len(items)}] {old_title[:40]}")
        print(f"          → {new_title[:40]}")

        if not preview:
            body, _ = _taobao_post("/product/update", shop_id, {
                "num_iid": str(ni), "title": new_title
            }, p)
            r = json.loads(body)
            status = "OK" if r.get("code") == 0 else f"FAIL: {r.get('msg','')}"
            print(f"          [{status}]")
        else:
            print("          [预览]")
    if preview:
        print("\n预览模式。去掉 preview 参数执行实际更新。")


def cmd_taobao_title_check(shop_id, platform=None):
    """标题质量检查 — 扫描所有在售商品标题，报告质量问题"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 标题质量检查 (shop_id={shop_id}, {p}) ===\n")

    body, _ = _taobao_get("/product/list", shop_id, "page=1&pagesize=200", p)
    products = json.loads(body)
    items = products.get("data", {}).get("data", {}).get("items", {}).get("item", [])
    if not items:
        print("无在售商品")
        return

    issues = []  # (num_iid, title, issue_list)
    total_too_short = 0
    total_too_long  = 0
    total_no_year   = 0
    total_dup_char  = 0

    for item in items:
        ni    = item.get("num_iid", "")
        title = item.get("title", "").strip()
        item_issues = []

        # 1. 长度检查
        if len(title) < 15:
            item_issues.append(f"偏短({len(title)}字)")
            total_too_short += 1
        if len(title) > 60:
            item_issues.append(f"超长({len(title)}字, 淘宝截断)")
            total_too_long += 1

        # 2. 年份关键词缺失
        has_year = any(yr in title for yr in ["2026", "2025", "新款", "春夏", "秋冬", "夏季", "冬季", "春季", "秋季"])
        if not has_year:
            item_issues.append("缺年份/季节词")
            total_no_year += 1

        # 3. 连续重复字符
        for dup in ["  ", "，，", "。。", "、、"]:
            if dup in title:
                item_issues.append(f"重复字符'{dup}'")
                total_dup_char += 1
                break

        if item_issues:
            issues.append((ni, title[:50], item_issues))

    print(f"共 {len(items)} 个商品, {len(issues)} 个存在问题\n")
    print(f"  偏短(<15字): {total_too_short}")
    print(f"  超长(>60字): {total_too_long}")
    print(f"  缺年份/季节: {total_no_year}")
    print(f"  重复字符:    {total_dup_char}\n")

    if issues:
        print("--- 问题详情 ---")
        for ni, title, item_issues in issues[:20]:
            print(f"  [{ni}] {title}")
            for i in item_issues:
                print(f"    ⚠ {i}")
        if len(issues) > 20:
            print(f"  ... 还有 {len(issues) - 20} 个")
    else:
        print("所有标题质量良好 ✓")


# ── taobao shortcut commands ─────────────────────

def cmd_taobao_dashboard(shop_id, platform=None):
    """店铺仪表盘 — 调用 shops + product/list + trade/list + rate/list 汇总"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 店铺仪表盘 (shop_id={shop_id}, {p}) ===\n")

    # 1. 店铺信息
    body, _ = _taobao_get("/shop/seller-info", shop_id, "", p)
    info = json.loads(body)
    if info.get("code") == 0:
        d = info["data"]["data"] if "data" in info.get("data", {}) else info.get("data", {})
        shop = d.get("shop", {})
        print(f"[店铺] {shop.get('title', 'N/A')}  sid={shop.get('sid', 'N/A')}")

    # 2. 商品概览
    body, _ = _taobao_get("/product/list", shop_id, "page=1&pagesize=1", p)
    prod = json.loads(body)
    if prod.get("code") == 0:
        items = prod.get("data", {}).get("data", {}).get("items", {}).get("item", [])
        total = prod.get("data", {}).get("data", {}).get("total_results", 0)
        print(f"[商品] 在售 {total} 个" + (f", 最新: {items[0]['title'][:30]}" if items else ""))

    # 3. 订单概览
    for status, label in [("", "全部"), ("WAIT_SELLER_SEND_GOODS", "待发货"), ("WAIT_BUYER_CONFIRM_GOODS", "待收货")]:
        body, _ = _taobao_get("/trade/list", shop_id, f"page=1&pagesize=1{'&status='+urllib.parse.quote(status) if status else ''}", p)
        trade = json.loads(body)
        if trade.get("code") == 0:
            n = trade.get("data", {}).get("data", {}).get("total_results", 0)
            print(f"[订单] {label}: {n} 笔")

    # 4. 评价概览
    for rtype, label in [("give", "收到评价"), ("get", "给出评价")]:
        body, _ = _taobao_get("/rate/list", shop_id, f"rate_type={rtype}&role=seller&page=1&page_size=1", p)
        rate = json.loads(body)
        if rate.get("code") == 0:
            n = rate.get("data", {}).get("data", {}).get("total_results", 0)
            print(f"[评价] {label}: {n} 条")

    print()

def cmd_taobao_quick_publish(shop_id, page="1", shop_type="taobao", platform=None):
    """快速选品发布 — 拉取今日新款第1个 → 极速发布"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 快速选品发布 (shop_id={shop_id}, {p}) ===\n")
    body, _ = api_request("GET", f"/product/today?page={page}", platform=p)
    today = json.loads(body)
    if today.get("code") != 0 or not today.get("data"):
        print("今日无可选新品")
        return
    item = today["data"][0]
    pid  = item.get("id", "")
    title = item.get("title", "")[:40]
    print(f"[选品] {pid} | {title}")
    body, _ = api_request("POST", "/product/fast-publish", data={
        "id": str(pid), "shop_id": str(shop_id), "shop_type": shop_type
    }, platform=p)
    result = json.loads(body)
    if result.get("code") == 0:
        print(f"[发布] 成功! job_id={result.get('data', {}).get('job_id', 'N/A')}")
    else:
        print(f"[发布] 失败: {result.get('msg', '')}")

def cmd_taobao_auto_ship(shop_id, express_code="YZPY", track_no="", platform=None):
    """批量发货 — 拉取待发货订单 → 逐个发货"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 批量发货 (shop_id={shop_id}, {p}) ===\n")
    body, _ = _taobao_get("/trade/list", shop_id, f"page=1&pagesize=20&status={urllib.parse.quote('WAIT_SELLER_SEND_GOODS')}", p)
    trades = json.loads(body)
    items = trades.get("data", {}).get("data", {}).get("trades", {}).get("trade", [])
    if not items:
        print("无待发货订单")
        return
    print(f"找到 {len(items)} 笔待发货订单\n")
    for i, t in enumerate(items):
        tid = t.get("tid", "")
        tn  = track_no or f"AUTO{int(time.time())}{i:03d}"
        body, _ = _taobao_post("/trade/ship", shop_id, {
            "tid": str(tid), "express_code": express_code, "track_no": tn,
        }, p)
        r = json.loads(body)
        status = "OK" if r.get("code") == 0 else f"FAIL: {r.get('msg','')}"
        print(f"  [{i+1}/{len(items)}] tid={tid} → {status}")

def cmd_taobao_batch_price(shop_id, adjustment, platform=None):
    """批量调价 — 拉取在售商品 → 全部按比例/绝对值调价
    adjustment: +10% 或 -50 或 99.00(固定价)"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 批量调价 (shop_id={shop_id}, {p}) adjustment={adjustment} ===\n")
    body, _ = _taobao_get("/product/list", shop_id, "page=1&pagesize=50", p)
    products = json.loads(body)
    items = products.get("data", {}).get("data", {}).get("items", {}).get("item", [])
    if not items:
        print("无在售商品")
        return
    is_pct = adjustment.endswith("%")
    val = float(adjustment.rstrip("%"))
    print(f"模式: {'百分比' if is_pct else '固定值/绝对值'} 参数={val}")
    print(f"找到 {len(items)} 个商品\n")
    for i, item in enumerate(items):
        ni = item.get("num_iid", "")
        old_price = float(item.get("price", 0))
        if adjustment.startswith("+") or adjustment.startswith("-"):
            new_price = old_price * (1 + val/100) if is_pct else old_price + val
        else:
            new_price = val if not is_pct else old_price
        new_price = round(max(new_price, 0.01), 2)
        body, _ = _taobao_post("/product/update-price", shop_id, {
            "num_iid": str(ni), "price": str(new_price),
        }, p)
        r = json.loads(body)
        status = "OK" if r.get("code") == 0 else f"FAIL: {r.get('msg','')}"
        print(f"  [{i+1}/{len(items)}] {item.get('title','')[:30]}  ¥{old_price}→¥{new_price}  {status}")

def cmd_taobao_rate_check(shop_id, platform=None):
    """评价巡检 — 查看差评告警"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 评价巡检 (shop_id={shop_id}, {p}) ===\n")
    for rtype, _, label in [("give", "seller", "收到"), ("get", "buyer", "给出")]:
        body, _ = _taobao_get("/rate/list", shop_id, f"rate_type={rtype}&page=1&page_size=50", p)
        rates = json.loads(body)
        items = rates.get("data", {}).get("data", {}).get("trade_rates", {}).get("trade_rate", [])
        neg = [r for r in items if r.get("result") in ("neutral", "bad")]
        print(f"[{label}评价] 共 {len(items)} 条, 差评/中评 {len(neg)} 条")
        for r in neg[:5]:
            print(f"  ❌ {r.get('item_title','')[:30]} | {r.get('content','')[:60]}")

def cmd_taobao_generate_titles(shop_id, platform=None):
    """标题批量生成 — product/list → product/detail → SubAgent → 对比展示
    不直接写入，先对比新旧标题供用户审核。"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 标题批量生成 (shop_id={shop_id}, {p}) ===\n")

    # 1. 获取在售商品列表
    body, _ = _taobao_get("/product/list", shop_id, "page=1&pagesize=50", p)
    products = json.loads(body)
    items = products.get("data", {}).get("data", {}).get("items", {}).get("item", [])
    if not items:
        print("无在售商品")
        return
    print(f"在售 {len(items)} 个商品，正在拉取属性...\n")

    # 2. 逐个拉取商品详情
    product_data = []
    for i, item in enumerate(items):
        ni = item.get("num_iid", "")
        print(f"  [{i+1}/{len(items)}] 拉取 {ni} ...", end=" ", flush=True)
        body, code = _taobao_get("/product/detail", shop_id, f"num_iid={ni}", p)
        if code != 200:
            # detail 失败，使用 list 数据降级
            title = item.get("title", "")
            desc_raw = str(item.get("desc", ""))
            raw_kw = re.findall(r'[\u4e00-\u9fa5]{2,4}', desc_raw)
            stop = {"可以", "提供", "注","大货已出","放心上架","数据包","颜色不齐"}
            desc_kw = list(dict.fromkeys(w for w in raw_kw if w not in stop))[:8]
            product_data.append({
                "num_iid": ni,
                "current_title": title,
                "category": "",
                "attributes": {},
                "price": float(item.get("price", 0)),
                "supplier": item.get("nick", ""),
                "desc_keywords": desc_kw,
                "outer_id": "",
            })
            print("跳过 (降级)")
            continue
        detail = json.loads(body)
        item_info = detail.get("data", {}).get("data", {}).get("item", {})
        if not item_info:
            # fallback: list 数据 + desc 提取关键词
            title = item.get("title", "")
            desc_raw = item.get("desc", "")
            # 提取描述关键词
            desc_kw = re.findall(r'[\u4e00-\u9fa5]{2,4}', str(desc_raw))[:5]
            product_data.append({
                "num_iid": ni,
                "current_title": title,
                "category": "",
                "attributes": {},
                "price": float(item.get("price", 0)),
                "supplier": item.get("nick", ""),
                "desc_keywords": desc_kw,
            })
            print("OK (降级)")
        else:
            # 解析淘宝属性 props_name → 结构化键值
            props_name = str(item_info.get("props_name", ""))
            attrs = {}
            for pair in props_name.split(";"):
                kv = pair.split(":", 1)
                if len(kv) == 2:
                    attrs[kv[0]] = kv[1]
            # 提取描述中的中文关键词（过滤字数<2的碎片 + 标点）
            desc_raw = str(item_info.get("desc", ""))
            raw_kw = re.findall(r'[\u4e00-\u9fa5]{2,6}', desc_raw)
            # 去重、过滤通用停用词
            stop = {"可以", "提供", "注","大货已出","放心上架","数据包","颜色不齐"}
            desc_kw = list(dict.fromkeys(w for w in raw_kw if w not in stop))[:8]
            # 获取 cid 对应的类目路径
            cid = str(item_info.get("cid", ""))
            product_data.append({
                "num_iid": ni,
                "current_title": str(item_info.get("title", "")),
                "category": cid,
                "attributes": attrs,
                "price": float(item_info.get("price", 0)),
                "supplier": str(item_info.get("nick", "")),
                "desc_keywords": desc_kw,
                "outer_id": str(item_info.get("outer_id", "")),
            })
            print("OK")

    if not product_data:
        print("\n无可用商品数据")
        return

    # 3. 输出为 JSON，供 Agent 发送给 SubAgent
    print(f"\n收集 {len(product_data)} 个商品数据，输入 SubAgent:\n")
    print(json.dumps({"products": product_data}, ensure_ascii=False, indent=2))

def cmd_taobao_daily_report(shop_id, platform=None):
    """每日经营日报"""
    p = platform or DEFAULT_PLATFORM
    today_str = time.strftime("%Y-%m-%d")
    print(f"=== 经营日报 {today_str} (shop_id={shop_id}, {p}) ===\n")

    # 店铺
    body, _ = _taobao_get("/shop/seller-info", shop_id, "", p)
    info = json.loads(body)
    shop_title = "N/A"
    if info.get("code") == 0:
        d = info.get("data", {}).get("data", {}) if "data" in info.get("data", {}) else info.get("data", {})
        shop_title = d.get("shop", {}).get("title", "N/A")
    print(f"店铺: {shop_title}")

    # 商品
    body, _ = _taobao_get("/product/list", shop_id, "page=1&pagesize=1", p)
    prod = json.loads(body)
    pc = prod.get("data", {}).get("data", {}).get("total_results", 0) if prod.get("code") == 0 else 0

    body, _ = _taobao_get("/product/inventory", shop_id, "page=1&pagesize=1", p)
    inv = json.loads(body)
    ic = inv.get("data", {}).get("data", {}).get("total_results", 0) if inv.get("code") == 0 else 0
    print(f"商品: 在售 {pc} | 仓库 {ic}")

    # 订单
    for status, label in [("all", "全部"), ("WAIT_SELLER_SEND_GOODS", "待发货"), ("WAIT_BUYER_CONFIRM_GOODS", "待收货"), ("TRADE_FINISHED", "已完成")]:
        s = "&status=" + urllib.parse.quote(status) if status != "all" else ""
        body, _ = _taobao_get("/trade/list", shop_id, f"page=1&pagesize=1{s}", p)
        t = json.loads(body)
        n = t.get("data", {}).get("data", {}).get("total_results", 0) if t.get("code") == 0 else 0
        print(f"订单: {label} {n} 笔")

    # 评价巡检
    for rtype, _, label in [("give", "seller", "收到"), ("get", "buyer", "给出")]:
        body, _ = _taobao_get("/rate/list", shop_id, f"rate_type={rtype}&page=1&page_size=50", p)
        rates = json.loads(body)
        items = rates.get("data", {}).get("data", {}).get("trade_rates", {}).get("trade_rate", []) if rates.get("code") == 0 else []
        neg = [r for r in items if r.get("result") in ("neutral", "bad")]
        print(f"评价: {label}评价 {len(items)} 条" + (f" ⚠差评{len(neg)}条" if neg else ""))

    print()

def usage():
    print(f"""用法: python driver.py <命令> [参数...]

命令:
  setup                                   设置各平台 API-Key
  today        [page] [platform]          今日新款列表 (默认 page=1, platform=k3)
  search       <关键词> [platform]         搜索产品
  shops        [platform]                 获取已绑定店铺列表
  publish      <ID[,ID...]> <shop_id> <shop_type> [platform]
                                          提交极速发布
  jobs         <产品ID> <shop_id> <shop_type> [platform]
                                          查看发布任务结果
  records      [日期]                     查看某天发布记录 (默认今天)
  record-list                             列出所有已保存的发布记录
  export       [开始日期] [结束日期]        导出 CSV 格式发布记录

  淘宝店铺管理:
  taobao shop-info <shop_id> [platform]   店铺基本信息
  taobao seller-info <shop_id> [platform] 卖家视角信息
  taobao user-info <shop_id> [platform]   卖家用户信息
  taobao product-list <shop_id> [page] [pagesize] [platform]    在售商品
  taobao product-inventory <shop_id> [page] [pagesize] [platform] 仓库商品
  taobao product-detail <shop_id> <num_iid> [platform] 商品详情
  taobao update-price <shop_id> <num_iid> <price> [platform] 改价
  taobao update-product <shop_id> <num_iid> [title] [desc] [platform] 更新商品信息
  taobao upshelf <shop_id> <num_iid> [num] [platform]    上架
  taobao downshelf <shop_id> <num_iid> [platform]       下架
  taobao delete <shop_id> <num_iid> [platform]          删除
  taobao trade-list <shop_id> [status] [page] [pagesize] [platform]  订单列表
  taobao trade-detail <shop_id> <tid> [platform]          订单详情
  taobao ship <shop_id> <tid> <express> <track_no> [platform] 发货
  taobao update-address <shop_id> <tid> [参数...] [platform]  改地址
  taobao memo-add <shop_id> <tid> <memo> [flag] [platform]    添加交易备注
  taobao memo-update <shop_id> <tid> <memo> [flag] [reset] [platform] 更新交易备注
  taobao oaid-merge <shop_id> <merge_order_ids...> [platform]  OAID订单合并
  taobao rate-list <shop_id> [rate_type] [role] [result] [page] [pagesize]  评价列表
  taobao rate-reply <shop_id> <oid> <reply> [platform]   评价回复
  taobao rate-add <shop_id> <tid> <result> [content] [oid] [platform] 新增评价
  taobao refund-list <shop_id> [status] [page] [pagesize] [platform]    退款列表
  taobao refund-detail <shop_id> <refund_id> [platform]                退款详情
  taobao refund-refuse <shop_id> <refund_id> <refund_version> [refuse_message] [platform] 拒绝退款
  taobao refund-agree <shop_id> <code> <refund_json> [message] [platform] 同意退款
  taobao returngoods-agree <shop_id> <refund_id> <refund_version> <seller_address_id> [refund_phase] [platform] 同意退货
  taobao refund-intercept <shop_id> <refund_id> <refund_version> [platform] 卖家发起拦截
  taobao deliveryintercept-feedback <shop_id> <refund_id> [logistic_status] [fail_reason] [platform] 物流拦截反馈
  taobao negotiatereturn <shop_id> <refund_id> <refund_version> [platform] 协商退货退款

  快捷命令:
  taobao dashboard <shop_id> [platform]              店铺仪表盘(商品/订单/评价概览)
  taobao quick-publish <shop_id> [page] [shop_type] [platform]  快速选品发布(今日新款→发布)
  taobao auto-ship <shop_id> [express_code] [track_no] [platform] 批量发货(待发货→发货)
  taobao batch-price <shop_id> <adjustment> [platform]  批量调价(+10%, -5, 99.0)
  taobao batch-title <shop_id> <mode> <value> [preview] [platform] 批量标题优化(prefix/suffix/replace)
  taobao generate-titles <shop_id> [platform]         标题AI生成(属性→SEO标题，需审核)
  taobao rate-check <shop_id> [platform]              评价巡检(差评告警)
  taobao title-check <shop_id> [platform]             标题质量巡检
  taobao daily-report <shop_id> [platform]            每日经营日报

平台:
  k3     - 开山网 (默认)
  bao66  - 包牛牛

注意: 不同平台的 API-Key 独立配置，互不通用。
     使用 setup 命令分别设置各平台的 Key。

API-Key 存储在: {CONFIG_FILE}
发布记录存储在: {RECORDS_DIR}/
""")


# ── main ─────────────────────────────────────────────────

def _resolve_platform(args, start_idx):
    """从命令行参数中提取 platform，返回 (platform, args_before_platform)。"""
    for i in range(start_idx, len(args)):
        if args[i] in PLATFORMS:
            return args[i]
    return None


def _exec_taobao(sub, args):
    """执行 taobao 子命令分发"""
    cmds = {
        "shop-info":         (cmd_taobao_shop_info,         1, 2),
        "seller-info":       (cmd_taobao_seller_info,       1, 2),
        "user-info":         (cmd_taobao_user_info,         1, 2),
        "product-list":      (cmd_taobao_product_list,      1, 4),
        "product-inventory": (cmd_taobao_product_inventory, 1, 4),
        "product-detail":    (cmd_taobao_product_detail,    2, 3),
        "update-product":    (cmd_taobao_update_product,    2, 5),
        "update-price":      (cmd_taobao_update_price,      3, 4),
        "upshelf":           (cmd_taobao_upshelf,           2, 4),
        "downshelf":         (cmd_taobao_downshelf,         2, 3),
        "delete":            (cmd_taobao_delete,            2, 3),
        "trade-list":        (cmd_taobao_trade_list,        1, 5),
        "trade-detail":      (cmd_taobao_trade_detail,      2, 3),
        "ship":              (cmd_taobao_ship,              4, 5),
        "update-address":    (cmd_taobao_update_address,    2, 8),
        "rate-list":         (cmd_taobao_rate_list,         1, 6),
        "rate-reply":        (cmd_taobao_rate_reply,        3, 4),
        "rate-add":          (cmd_taobao_rate_add,          3, 7),
        "memo-add":          (cmd_taobao_memo_add,          3, 5),
        "memo-update":       (cmd_taobao_memo_update,       3, 6),
        "oaid-merge":        (cmd_taobao_oaid_merge,        2, 3),
        "refund-list":       (cmd_taobao_refund_list,       1, 5),
        "refund-detail":     (cmd_taobao_refund_detail,     2, 3),
        "refund-refuse":     (cmd_taobao_refund_refuse,     3, 5),
        "refund-agree":      (cmd_taobao_refund_agree,      3, 5),
        "returngoods-agree":             (cmd_taobao_returngoods_agree,      4, 6),
        "refund-intercept":              (cmd_taobao_refund_intercept,       3, 4),
        "deliveryintercept-feedback":    (cmd_taobao_deliveryintercept_feedback, 2, 5),
        "negotiatereturn":               (cmd_taobao_negotiatereturn,        3, 4),
        # 快捷命令
        "dashboard":                     (cmd_taobao_dashboard,              1, 2),
        "quick-publish":                 (cmd_taobao_quick_publish,          1, 4),
        "auto-ship":                     (cmd_taobao_auto_ship,              1, 4),
        "batch-price":                   (cmd_taobao_batch_price,            2, 3),
        "batch-title":                   (cmd_taobao_batch_title,            3, 5),
        "generate-titles":               (cmd_taobao_generate_titles,        1, 2),
        "rate-check":                    (cmd_taobao_rate_check,             1, 2),
        "daily-report":                  (cmd_taobao_daily_report,           1, 2),
    }
    if sub not in cmds:
        print(f"错误: 未知 taobao 子命令 '{sub}'")
        print("可用: shop-info, seller-info, user-info, product-list, product-inventory,")
        print("      product-detail, update-price, upshelf, downshelf, delete,")
        print("      trade-list, trade-detail, ship, update-address,")
        print("      memo-add, memo-update, oaid-merge,")
        print("      rate-list, rate-reply, rate-add,")
        print("      refund-list, refund-detail, refund-refuse, refund-agree,")
        print("      returngoods-agree, refund-intercept, deliveryintercept-feedback, negotiatereturn")
        print("快捷命令:")
        print("      dashboard, quick-publish, auto-ship, batch-price, batch-title, generate-titles, rate-check, daily-report, title-check")
        sys.exit(1)

    func, min_args, max_args = cmds[sub]
    if len(args) < min_args:
        print(f"错误: taobao {sub} 至少需要 {min_args} 个参数")
        sys.exit(1)

    platform = None
    cmd_args = list(args)
    if cmd_args and cmd_args[-1] in PLATFORMS:
        platform = cmd_args.pop()
    elif cmd_args and len(cmd_args) >= min_args and _resolve_platform(cmd_args, 0):
        platform = _resolve_platform(cmd_args, 0)

    if sub == "shop-info":
        nick = cmd_args[1] if len(cmd_args) > 1 else ""
        cmd_taobao_shop_info(cmd_args[0], nick, platform)
    elif sub == "seller-info":
        cmd_taobao_seller_info(cmd_args[0], platform)
    elif sub == "user-info":
        cmd_taobao_user_info(cmd_args[0], platform)
    elif sub == "product-list":
        cmd_taobao_product_list(cmd_args[0], cmd_args[1] if len(cmd_args) > 1 else "1", cmd_args[2] if len(cmd_args) > 2 else "50", platform)
    elif sub == "product-inventory":
        cmd_taobao_product_inventory(cmd_args[0], cmd_args[1] if len(cmd_args) > 1 else "1", cmd_args[2] if len(cmd_args) > 2 else "50", platform)
    elif sub == "product-detail":
        cmd_taobao_product_detail(cmd_args[0], cmd_args[1], platform)
    elif sub == "update-price":
        cmd_taobao_update_price(cmd_args[0], cmd_args[1], cmd_args[2], platform)
    elif sub == "upshelf":
        cmd_taobao_upshelf(cmd_args[0], cmd_args[1], cmd_args[2] if len(cmd_args) > 2 else "100", platform)
    elif sub == "downshelf":
        cmd_taobao_downshelf(cmd_args[0], cmd_args[1], platform)
    elif sub == "delete":
        cmd_taobao_delete(cmd_args[0], cmd_args[1], platform)
    elif sub == "trade-list":
        cmd_taobao_trade_list(cmd_args[0], cmd_args[1] if len(cmd_args) > 1 else "", cmd_args[2] if len(cmd_args) > 2 else "1", cmd_args[3] if len(cmd_args) > 3 else "40", platform)
    elif sub == "trade-detail":
        cmd_taobao_trade_detail(cmd_args[0], cmd_args[1], platform)
    elif sub == "ship":
        cmd_taobao_ship(cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3], platform)
    elif sub == "update-address":
        cmd_taobao_update_address(cmd_args[0], cmd_args[1],
                                  cmd_args[2] if len(cmd_args) > 2 else "",
                                  cmd_args[3] if len(cmd_args) > 3 else "",
                                  cmd_args[4] if len(cmd_args) > 4 else "",
                                  cmd_args[5] if len(cmd_args) > 5 else "",
                                  cmd_args[6] if len(cmd_args) > 6 else "",
                                  cmd_args[7] if len(cmd_args) > 7 else "",
                                  platform)
    elif sub == "rate-list":
        cmd_taobao_rate_list(cmd_args[0],
                             cmd_args[1] if len(cmd_args) > 1 else "give",
                             cmd_args[2] if len(cmd_args) > 2 else "seller",
                             cmd_args[3] if len(cmd_args) > 3 else "",
                             cmd_args[4] if len(cmd_args) > 4 else "1",
                             cmd_args[5] if len(cmd_args) > 5 else "40",
                             platform)
    elif sub == "rate-reply":
        cmd_taobao_rate_reply(cmd_args[0], cmd_args[1], cmd_args[2], platform)
    elif sub == "rate-add":
        cmd_taobao_rate_add(cmd_args[0], cmd_args[1], cmd_args[2],
                            cmd_args[3] if len(cmd_args) > 3 else "",
                            cmd_args[4] if len(cmd_args) > 4 else "",
                            platform)
    elif sub == "memo-add":
        cmd_taobao_memo_add(cmd_args[0], cmd_args[1], cmd_args[2],
                            cmd_args[3] if len(cmd_args) > 3 else "0",
                            platform)
    elif sub == "memo-update":
        cmd_taobao_memo_update(cmd_args[0], cmd_args[1], cmd_args[2],
                               cmd_args[3] if len(cmd_args) > 3 else "0",
                               cmd_args[4] if len(cmd_args) > 4 else "false",
                               platform)
    elif sub == "oaid-merge":
        merge_ids = " ".join(cmd_args[1:]) if len(cmd_args) > 1 else ""
        cmd_taobao_oaid_merge(cmd_args[0], merge_ids, platform)
    elif sub == "refund-list":
        cmd_taobao_refund_list(cmd_args[0],
                               cmd_args[1] if len(cmd_args) > 1 else "",
                               cmd_args[2] if len(cmd_args) > 2 else "1",
                               cmd_args[3] if len(cmd_args) > 3 else "40",
                               platform)
    elif sub == "refund-detail":
        cmd_taobao_refund_detail(cmd_args[0], cmd_args[1], platform)
    elif sub == "refund-refuse":
        cmd_taobao_refund_refuse(cmd_args[0], cmd_args[1], cmd_args[2],
                                 cmd_args[3] if len(cmd_args) > 3 else "",
                                 platform)
    elif sub == "refund-agree":
        cmd_taobao_refund_agree(cmd_args[0], cmd_args[1], cmd_args[2],
                                cmd_args[3] if len(cmd_args) > 3 else "",
                                platform)
    elif sub == "returngoods-agree":
        cmd_taobao_returngoods_agree(cmd_args[0], cmd_args[1], cmd_args[2], cmd_args[3],
                                     cmd_args[4] if len(cmd_args) > 4 else "onsale",
                                     platform)
    elif sub == "refund-intercept":
        cmd_taobao_refund_intercept(cmd_args[0], cmd_args[1], cmd_args[2], platform)
    elif sub == "deliveryintercept-feedback":
        cmd_taobao_deliveryintercept_feedback(cmd_args[0], cmd_args[1],
                                              cmd_args[2] if len(cmd_args) > 2 else "",
                                              cmd_args[3] if len(cmd_args) > 3 else "",
                                              platform)
    elif sub == "negotiatereturn":
        cmd_taobao_negotiatereturn(cmd_args[0], cmd_args[1], cmd_args[2], platform)
    elif sub == "dashboard":
        cmd_taobao_dashboard(cmd_args[0], platform)
    elif sub == "quick-publish":
        cmd_taobao_quick_publish(cmd_args[0],
                                 cmd_args[1] if len(cmd_args) > 1 else "1",
                                 cmd_args[2] if len(cmd_args) > 2 else "taobao",
                                 platform)
    elif sub == "auto-ship":
        cmd_taobao_auto_ship(cmd_args[0],
                             cmd_args[1] if len(cmd_args) > 1 else "YZPY",
                             cmd_args[2] if len(cmd_args) > 2 else "",
                             platform)
    elif sub == "batch-price":
        cmd_taobao_batch_price(cmd_args[0], cmd_args[1], platform)
    elif sub == "batch-title":
        preview = cmd_args[3] if len(cmd_args) > 3 else "true"
        cmd_taobao_batch_title(cmd_args[0], cmd_args[1], cmd_args[2],
                               preview.lower() != "false", platform)
    elif sub == "generate-titles":
        cmd_taobao_generate_titles(cmd_args[0], platform)
    elif sub == "rate-check":
        cmd_taobao_rate_check(cmd_args[0], platform)
    elif sub == "daily-report":
        cmd_taobao_daily_report(cmd_args[0], platform)


def main():
    ensure_dirs()
    args = sys.argv[1:]

    if not args or args[0] in ("help", "--help", "-h"):
        usage()
        return

    cmd = args[0]

    # 不需要 api-key 的命令
    no_key_cmds = {"help", "--help", "-h", "setup", "record-list", "records", "export"}

    if cmd not in no_key_cmds:
        # 从参数中推断目标平台，预检对应 key
        platform = _resolve_platform(args, 1)
        if not platform:
            platform = DEFAULT_PLATFORM
        if not load_api_key(platform):
            prompt_api_key(platform)

    try:
        if cmd == "setup":
            cmd_setup()
        elif cmd == "today":
            cmd_today(args[1] if len(args) > 1 else "1",
                      args[2] if len(args) > 2 else None)
        elif cmd == "search":
            if len(args) < 2:
                print("错误: search 需要关键词参数")
                sys.exit(1)
            cmd_search(args[1], args[2] if len(args) > 2 else None)
        elif cmd == "shops":
            cmd_shops(args[1] if len(args) > 1 else None)
        elif cmd == "publish":
            if len(args) < 4:
                print("错误: publish 需要 产品ID shop_id shop_type [platform]")
                print("提示: 先用 shops 命令获取店铺信息")
                sys.exit(1)
            cmd_publish(args[1], args[2], args[3],
                        args[4] if len(args) > 4 else None)
        elif cmd == "jobs":
            if len(args) < 4:
                print("错误: jobs 需要 产品ID shop_id shop_type [platform]")
                sys.exit(1)
            cmd_jobs(args[1], args[2], args[3],
                     args[4] if len(args) > 4 else None)
        elif cmd == "records":
            cmd_records(args[1] if len(args) > 1 else None)
        elif cmd == "record-list":
            cmd_record_list()
        elif cmd == "export":
            cmd_record_export(args[1] if len(args) > 1 else None,
                              args[2] if len(args) > 2 else None)
        elif cmd == "taobao":
            if len(args) < 2:
                print("错误: taobao 需要子命令")
                sys.exit(1)
            sub = args[1]
            _exec_taobao(sub, args[2:])
        else:
            print(f"未知命令: {cmd}")
            usage()
            sys.exit(1)
    except Exception as e:
        print(f">>> 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
