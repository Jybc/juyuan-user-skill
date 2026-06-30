#!/usr/bin/env python3
"""K3 产品展示页生成器（huashu-design 平台优先模板）。纯 stdlib，读 config。"""
import json, os, sys, urllib.request, base64
from datetime import datetime

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "k3-publish")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config")

PLATFORM = {
    "k3":    {"bg": "#D4302B", "name": "开山网 K3"},
    "bao66": {"bg": "#1A6FE0", "name": "包牛牛 Bao66"},
}

def load_api_key(platform="k3"):
    keys = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.startswith("API_KEY") and v:
                        keys[k] = v
    return keys.get(f"API_KEY_{platform}", keys.get("API_KEY"))

def _fetch(path, platform):
    api_key = load_api_key(platform)
    if not api_key:
        print("错误: 未配置 API Key", file=sys.stderr)
        sys.exit(1)
    url = f"https://open.jybc.com.cn/agent{path}{'&' if '?' in path else '?'}api_key={api_key}"
    req = urllib.request.Request(url, headers={"User-Agent": "juyuan-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())
    if body.get("code") != 0:
        print(f"API 错误: {body.get('msg')}", file=sys.stderr)
        sys.exit(1)
    return body["data"]

def fetch_today(page=1, platform="k3"):
    return _fetch(f"/product/today?page={page}&platform={platform}", platform)

def fetch_search(keyword, platform="k3"):
    wd = urllib.parse.quote(keyword)
    return _fetch(f"/product/search?wd={wd}&platform={platform}", platform)

def download_images(data, img_dir):
    os.makedirs(img_dir, exist_ok=True)
    b64 = {}
    for item in data:
        fn = item["index_image"].split("/")[-1]
        local = os.path.join(img_dir, fn)
        if not os.path.exists(local) or os.path.getsize(local) == 0:
            req = urllib.request.Request(item["index_image"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                with open(local, "wb") as f:
                    f.write(r.read())
        with open(local, "rb") as f:
            b64[fn] = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    return b64

def cards_html(data, b64):
    out = ""
    for i, item in enumerate(data):
        fn = item["index_image"].split("/")[-1]
        t = item["product_title"]
        if t == "无":
            t = ""
        out += f'''      <article class="card" style="animation-delay:{i*40}ms">
        <div class="card-img">
          <img src="{b64[fn]}" loading="lazy">
          <span class="card-price">¥{item['price']}</span>
        </div>
        <div class="card-body">
          <span class="card-id">{item['supplier_title']}&{item['article_number']}</span>
          <p class="card-title">{t or ""}</p>
        </div>
      </article>
'''
    return out

CSS = r'''
  :root {
    --brand: #E02D2D;
    --bg: #f4f4f4;
    --card-bg: #fff;
    --text: #222;
    --muted: #999;
  }
  *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    -webkit-font-smoothing: antialiased;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
  }

  /* ── 吸顶品牌栏 ── */
  .topbar {
    position: sticky; top: 0; z-index: 100;
    background: var(--card-bg);
    border-bottom: 1px solid #eee;
    padding: 12px 16px;
    display: flex; align-items: center; gap: 10px;
  }
  .topbar .brand {
    font-size: 18px; font-weight: 700; color: var(--brand); letter-spacing: -0.02em;
  }
  .topbar .sep { color: #ddd; font-weight: 300; }
  .topbar .context { font-size: 13px; color: var(--muted); flex: 1; }
  .topbar .count {
    font-size: 12px; color: var(--muted); background: var(--bg);
    padding: 3px 10px; border-radius: 10px;
  }

  /* ── 内容网格 ── */
  .grid {
    padding: 10px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  /* ── 产品卡片 ── */
  .card {
    background: var(--card-bg);
    border-radius: 10px;
    overflow: hidden;
    opacity: 0;
    animation: cardIn 0.35s ease forwards;
  }
  @keyframes cardIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .card-img {
    position: relative;
    background: #f8f8f8;
    overflow: hidden;
  }
  .card-img img {
    width: 100%; aspect-ratio: 1; object-fit: cover; display: block;
    transition: transform 0.3s ease;
  }
  .card:active .card-img img { transform: scale(1.04); }
  .card-price {
    position: absolute; bottom: 8px; left: 8px;
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    color: #fff; font-size: 16px; font-weight: 700;
    padding: 3px 10px; border-radius: 6px;
    letter-spacing: -0.01em; line-height: 1.4;
  }
  .card-body { padding: 10px; }
  .card-id { font-size: 11px; color: var(--muted); font-weight: 500; }
  .card-title {
    font-size: 13px; font-weight: 600; line-height: 1.35; margin-top: 4px;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }

  /* ── 空态 ── */
  .empty { text-align: center; padding: 80px 20px; }
  .empty p { font-size: 16px; color: #ccc; }

  /* ── Footer ── */
  footer { text-align: center; padding: 24px 16px 48px; font-size: 12px; color: #ccc; }

  /* ── 桌面端 ── */
  @media (min-width: 768px) {
    .topbar { padding: 14px 24px; max-width: 1200px; margin: 0 auto; border: none; border-bottom: 1px solid #eee; }
    .grid { padding: 16px; grid-template-columns: repeat(4, 1fr); gap: 16px; max-width: 1200px; margin: 0 auto; }
    .card { border-radius: 12px; }
    .card-price { font-size: 18px; padding: 4px 12px; }
    .card-body { padding: 12px; }
  }
  @media (min-width: 1024px) {
    .grid { grid-template-columns: repeat(5, 1fr); }
  }
'''

def build_html(ctx, platform):
    pc = PLATFORM.get(platform, PLATFORM["k3"])
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<title>{pc["name"]} · {ctx["label"]}</title>
<style>:root {{ --brand: {pc["bg"]}; }}
{CSS}
</style>
</head>
<body>
  <header class="topbar">
    <span class="brand">{pc["name"]}</span>
    <span class="sep">·</span>
    <span class="context">{ctx["label"]}</span>
    <span class="count">{ctx["count"]}</span>
  </header>
  <main class="grid">
{ctx["body"]}
  </main>
  <footer>{pc["name"]} · 聚源发</footer>
</body>
</html>'''

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
    img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "k3-images")

    if cmd == "search":
        keyword = sys.argv[2]
        platform = sys.argv[3] if len(sys.argv) > 3 else "k3"
        out = sys.argv[4] if len(sys.argv) > 4 else f"开山网-搜索-{keyword}.html"
        data = fetch_search(keyword, platform)
        b64 = download_images(data, img_dir)
        html = build_html({"label": f"搜索「{keyword}」", "count": f"{len(data)}个结果", "body": cards_html(data, b64)}, platform)
    else:
        page = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        platform = sys.argv[2] if len(sys.argv) > 2 else "k3"
        out = sys.argv[3] if len(sys.argv) > 3 else None
        data = fetch_today(page, platform)
        b64 = download_images(data, img_dir)
        today = datetime.now().strftime("%m月%d日")
        pg = f"第{page}页 · " if page > 1 else ""
        html = build_html({"label": f"{pg}今日新款 · {today}", "count": f"{len(data)}款", "body": cards_html(data, b64)}, platform)
        if not out:
            today_str = datetime.now().strftime("%Y-%m-%d")
            out = f"开山网-今日新款-{today_str}.html"

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK {out} ({len(data)} items)")

if __name__ == "__main__":
    main()
