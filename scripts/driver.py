#!/usr/bin/env python3
"""K3 极速发布平台 API 驱动。纯 stdlib，无需 pip install，跨平台可用。"""
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

BASE_URL = "https://open.jybc.com.cn/agent"
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


def api_request(method, path, data=None, platform=None):
    """发送 API 请求，自动使用匹配平台的 API Key。认证方式：api_key 作为 URL 查询参数。"""
    api_key = get_api_key(platform)
    sep = "&" if "?" in path else "?"
    url = f"{BASE_URL}{path}{sep}api_key={api_key}"
    headers = {"User-Agent": USER_AGENT}

    if data:
        encoded = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return body, resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return body, e.code
    except urllib.error.URLError as e:
        return f'{{"error": "{e.reason}"}}', 0


def pretty_print(body):
    try:
        parsed = json.loads(body)
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except (json.JSONDecodeError, ValueError):
        print(body)


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
    p = platform or DEFAULT_PLATFORM
    print(f"=== 搜索产品: {keyword} (platform={p}) ===")
    encoded = urllib.parse.quote(keyword)
    path = _add_platform(f"/product/search?wd={encoded}", platform)
    body, code = api_request("GET", path, platform=p)
    pretty_print(body)


def cmd_shops(platform=None):
    """获取已绑定店铺列表"""
    p = platform or DEFAULT_PLATFORM
    print(f"=== 店铺列表 (platform={p}) ===")
    path = _add_platform("/user/shops", platform)
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


# ── usage ────────────────────────────────────────────────

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
        else:
            print(f"未知命令: {cmd}")
            usage()
            sys.exit(1)
    except Exception as e:
        print(f">>> 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
