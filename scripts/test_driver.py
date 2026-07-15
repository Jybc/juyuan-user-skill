#!/usr/bin/env python3
"""K3 极速发布 driver.py 单元测试。纯 stdlib，无需 pip install。"""
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
import urllib.request
import urllib.error

# 导入被测模块
from driver import (
    PLATFORMS, DEFAULT_PLATFORM, BASE_URL,
    load_all_keys, load_api_key, save_api_key,
    get_api_key, api_request, pretty_print, _add_platform,
    cmd_setup, cmd_show_keys, cmd_today, cmd_search, cmd_shops,
    cmd_publish, cmd_jobs, cmd_records, cmd_record_list, cmd_record_export,
    _resolve_platform, ensure_dirs, prompt_api_key, usage,
    # taobao 单命令
    cmd_taobao_shop_info, cmd_taobao_seller_info, cmd_taobao_user_info,
    cmd_taobao_product_list, cmd_taobao_product_inventory, cmd_taobao_product_detail,
    cmd_taobao_update_price, cmd_taobao_update_product,
    cmd_taobao_upshelf, cmd_taobao_downshelf, cmd_taobao_delete,
    cmd_taobao_trade_list, cmd_taobao_trade_detail,
    cmd_taobao_ship, cmd_taobao_update_address,
    cmd_taobao_memo_add, cmd_taobao_memo_update, cmd_taobao_oaid_merge,
    cmd_taobao_rate_list, cmd_taobao_rate_reply, cmd_taobao_rate_add,
    cmd_taobao_refund_list, cmd_taobao_refund_detail, cmd_taobao_refund_refuse,
    cmd_taobao_refund_agree, cmd_taobao_returngoods_agree,
    cmd_taobao_refund_intercept, cmd_taobao_deliveryintercept_feedback, cmd_taobao_negotiatereturn,
    # 快捷命令
    cmd_taobao_dashboard, cmd_taobao_daily_report, cmd_taobao_quick_publish,
    cmd_taobao_auto_ship, cmd_taobao_batch_price, cmd_taobao_batch_title,
    cmd_taobao_rate_check, cmd_taobao_title_check,
)
import driver  # 用于 patch 模块属性


class BaseTestCase(unittest.TestCase):
    """所有测试的基类：提供临时目录和 stdout/stderr 捕获。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.config_dir = self._tmp.name
        self.config_file = os.path.join(self.config_dir, "config")
        self.records_dir = os.path.join(self.config_dir, "records")

        # Patch 模块级别的路径常量
        self._patchers = [
            unittest.mock.patch.object(driver, "CONFIG_DIR", self.config_dir),
            unittest.mock.patch.object(driver, "CONFIG_FILE", self.config_file),
            unittest.mock.patch.object(driver, "RECORDS_DIR", self.records_dir),
        ]
        for p in self._patchers:
            p.start()

        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.records_dir, exist_ok=True)

    def tearDown(self):
        for p in self._patchers:
            p.stop()
        self._tmp.cleanup()

    def _capture_stdout(self, fn, *args, **kwargs):
        """运行 fn 并返回 stdout 输出。"""
        buf = io.StringIO()
        with unittest.mock.patch("sys.stdout", buf):
            fn(*args, **kwargs)
        return buf.getvalue()

    def _write_config(self, lines):
        """写入临时 config 文件。"""
        with open(self.config_file, "w") as f:
            for line in lines:
                f.write(line + "\n")


# ── Config 读写测试 ──────────────────────────────────────

class TestLoadAllKeys(BaseTestCase):

    def test_empty_file(self):
        self._write_config([])
        self.assertEqual(load_all_keys(), {})

    def test_no_config_file(self):
        # 确保 config 文件不存在
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.assertEqual(load_all_keys(), {})

    def test_platform_keys(self):
        self._write_config([
            "API_KEY_k3=sk-k3-key-123",
            "API_KEY_bao66=sk-bao66-key-456",
        ])
        keys = load_all_keys()
        self.assertEqual(keys["API_KEY_k3"], "sk-k3-key-123")
        self.assertEqual(keys["API_KEY_bao66"], "sk-bao66-key-456")

    def test_ignores_empty_values_and_non_api_key(self):
        self._write_config([
            "API_KEY_k3=",
            "API_KEY_bao66=valid",
            "SOME_OTHER=value",
        ])
        keys = load_all_keys()
        self.assertNotIn("API_KEY_k3", keys)  # 空值跳过
        self.assertIn("API_KEY_bao66", keys)
        self.assertNotIn("SOME_OTHER", keys)


class TestLoadApiKey(BaseTestCase):

    def test_load_platform_specific(self):
        self._write_config([
            "API_KEY_k3=sk-k3-123",
            "API_KEY_bao66=sk-bao66-456",
        ])
        self.assertEqual(load_api_key("k3"), "sk-k3-123")
        self.assertEqual(load_api_key("bao66"), "sk-bao66-456")

    def test_fallback_to_generic(self):
        self._write_config(["API_KEY=sk-generic-999"])
        self.assertEqual(load_api_key("k3"), "sk-generic-999")
        self.assertEqual(load_api_key("bao66"), "sk-generic-999")

    def test_platform_takes_priority_over_generic(self):
        self._write_config([
            "API_KEY=sk-generic-999",
            "API_KEY_k3=sk-k3-123",
        ])
        self.assertEqual(load_api_key("k3"), "sk-k3-123")
        self.assertEqual(load_api_key("bao66"), "sk-generic-999")  # bao66 没有专属，回退

    def test_platform_none_returns_generic(self):
        self._write_config(["API_KEY=sk-generic-999"])
        self.assertEqual(load_api_key(None), "sk-generic-999")

    def test_no_key_returns_none(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.assertIsNone(load_api_key("k3"))


class TestSaveApiKey(BaseTestCase):

    def test_save_platform_key(self):
        save_api_key("sk-k3-new", "k3")
        self.assertEqual(load_api_key("k3"), "sk-k3-new")

    def test_save_multiple_platform_keys_independent(self):
        save_api_key("sk-k3-1", "k3")
        save_api_key("sk-bao66-2", "bao66")
        self.assertEqual(load_api_key("k3"), "sk-k3-1")
        self.assertEqual(load_api_key("bao66"), "sk-bao66-2")

    def test_save_generic_key_clears_platform_keys(self):
        save_api_key("sk-k3-old", "k3")
        save_api_key("sk-generic")
        # 平台专属 key 被清除，但 load_api_key 回退到通用 key
        self.assertEqual(load_api_key("k3"), "sk-generic")
        self.assertEqual(load_api_key(None), "sk-generic")
        # 验证 config 文件中没有 API_KEY_k3
        keys = load_all_keys()
        self.assertNotIn("API_KEY_k3", keys)
        self.assertIn("API_KEY", keys)

    def test_update_existing_platform_key(self):
        self._write_config(["API_KEY_k3=sk-old"])
        save_api_key("sk-new", "k3")
        self.assertEqual(load_api_key("k3"), "sk-new")


class TestGetApiKey(BaseTestCase):

    def test_returns_existing_key(self):
        self._write_config(["API_KEY_k3=sk-k3-123"])
        self.assertEqual(get_api_key("k3"), "sk-k3-123")

    def test_prompts_when_missing(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        with unittest.mock.patch("sys.stdin", io.StringIO("user-input-key\n")):
            result = get_api_key("k3")
        self.assertEqual(result, "user-input-key")


# ── URL / 工具函数测试 ───────────────────────────────────

class TestAddPlatform(unittest.TestCase):

    def test_add_to_clean_path(self):
        self.assertEqual(
            _add_platform("/product/today", "k3"),
            "/product/today?platform=k3",
        )

    def test_add_to_path_with_query(self):
        self.assertEqual(
            _add_platform("/product/today?page=1", "k3"),
            "/product/today?page=1&platform=k3",
        )

    def test_default_platform(self):
        self.assertEqual(
            _add_platform("/user/shops"),
            "/user/shops?platform=k3",
        )

    def test_explicit_platform_overrides_default(self):
        self.assertEqual(
            _add_platform("/user/shops", "bao66"),
            "/user/shops?platform=bao66",
        )


class TestPrettyPrint(unittest.TestCase):

    def test_valid_json(self):
        buf = io.StringIO()
        with unittest.mock.patch("sys.stdout", buf):
            pretty_print('{"a": 1, "b": "你好"}')
        output = buf.getvalue()
        self.assertIn('"a": 1', output)
        self.assertIn("你好", output)

    def test_invalid_json_falls_through(self):
        buf = io.StringIO()
        with unittest.mock.patch("sys.stdout", buf):
            pretty_print("not json at all")
        self.assertEqual(buf.getvalue().strip(), "not json at all")


class TestResolvePlatform(unittest.TestCase):

    def test_finds_platform(self):
        self.assertEqual(_resolve_platform(["today", "1", "bao66"], 1), "bao66")

    def test_returns_none_if_not_found(self):
        self.assertIsNone(_resolve_platform(["today", "1"], 1))

    def test_respects_start_idx(self):
        # platform 作为命令本身不算
        self.assertIsNone(_resolve_platform(["k3", "today"], 1))

    def test_first_match_only(self):
        self.assertEqual(_resolve_platform(["publish", "123", "k3", "bao66"], 1), "k3")


# ── API 请求测试 ─────────────────────────────────────────

class TestApiRequest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test-key"])

    def _mock_response(self, body, status=200):
        """创建一个 mock HTTPResponse。"""
        resp = unittest.mock.MagicMock()
        resp.__enter__ = unittest.mock.MagicMock(return_value=resp)
        resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        resp.read.return_value = body.encode()
        resp.status = status
        return resp

    def test_get_request(self):
        mock_resp = self._mock_response('{"ok": true}')
        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            body, code = api_request("GET", "/product/today?page=1&platform=k3", platform="k3")

        self.assertEqual(code, 200)
        self.assertEqual(body, '{"ok": true}')
        mock_open.assert_called_once()

    def test_post_request_with_data(self):
        mock_resp = self._mock_response('{"job-id": 42}')
        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            body, code = api_request("POST", "/product/fast-publish",
                                     data={"platform": "k3", "product_id": "100"},
                                     platform="k3")

        self.assertEqual(code, 200)
        self.assertIn("42", body)
        # 验证 data 被编码并发送
        call_args = mock_open.call_args[0][0]
        self.assertIn(b"product_id=100", call_args.data)

    def test_http_error(self):
        error = urllib.error.HTTPError(
            "http://fake", 401, "Unauthorized", {}, io.BytesIO(b'{"error": "unauthorized"}')
        )
        with unittest.mock.patch("urllib.request.urlopen", side_effect=error):
            body, code = api_request("GET", "/user/shops?platform=k3", platform="k3")

        self.assertEqual(code, 401)
        self.assertIn("unauthorized", body)

    def test_url_error(self):
        error = urllib.error.URLError("connection refused")
        with unittest.mock.patch("urllib.request.urlopen", side_effect=error):
            body, code = api_request("GET", "/product/today?page=1&platform=k3", platform="k3")

        self.assertEqual(code, 0)
        self.assertIn("connection refused", body)
        self.assertIn("retries", body)  # v1.1: 返回重试次数

    def test_retry_on_502(self):
        """502/503/504 自动重试"""
        error_502 = urllib.error.HTTPError(
            "http://fake", 502, "Bad Gateway", {}, io.BytesIO(b'{"error": "gateway"}')
        )
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"ok": true}'
        mock_resp.status = 200

        # 第一次 502，第二次成功
        with unittest.mock.patch("urllib.request.urlopen", side_effect=[error_502, mock_resp]):
            body, code = api_request("GET", "/product/today?page=1&platform=k3", platform="k3")

        self.assertEqual(code, 200)
        self.assertIn("ok", body)


# ── 命令函数测试 ─────────────────────────────────────────

class TestCmdShowKeys(BaseTestCase):

    def test_no_keys(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        output = self._capture_stdout(cmd_show_keys)
        self.assertIn("(无)", output)

    def test_show_keys_masked(self):
        self._write_config(["API_KEY_k3=sk-test-key-very-long"])
        output = self._capture_stdout(cmd_show_keys)
        # 短 key 显示全量
        self._write_config(["API_KEY_k3=sk-1234567890-very-long-tail"])
        output = self._capture_stdout(cmd_show_keys)
        self.assertIn("sk-1234567...", output)  # 长 key 脱敏


class TestCmdToday(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def test_today_default(self):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'[{"id": 1}]'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_today, page="1", platform=None)

        self.assertIn("platform=k3", output)
        self.assertIn("page=1", output)
        self.assertIn('"id": 1', output)

    def test_today_with_platform(self):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'[]'
        mock_resp.status = 200

        self._write_config(["API_KEY_bao66=sk-bao"])
        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_today, page="1", platform="bao66")

        self.assertIn("platform=bao66", output)


class TestCmdSearch(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def test_search_keyword(self):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'[{"title": "test product"}]'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_search, keyword="运动鞋", platform=None)

        self.assertIn("运动鞋", output)
        self.assertIn("test product", output)

    def test_search_short_keyword_rejected(self):
        """搜索词短于 2 字符应拒绝"""
        output = self._capture_stdout(cmd_search, keyword="鞋", platform=None)
        self.assertIn("code", output)
        self.assertIn("过短", output)

    def test_search_html_stripped(self):
        """HTML 标签应被剥离"""
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'[]'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_search, keyword="<script>凉鞋</script>", platform=None)

        self.assertNotIn("<script>", output)
        self.assertIn("凉鞋", output)

    def test_search_long_keyword_truncated(self):
        """超过 20 字符应自动截断"""
        long_kw = "这是一个超过二十个字符的超长搜索关键词测试输入"
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'[]'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_search, keyword=long_kw, platform=None)

        self.assertIn("截断", output)
        self.assertNotIn(long_kw, output)


class TestCmdShops(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def test_shops_default(self):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'[{"shop_id": "001", "shop_type": "taobao"}]'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_shops)

        self.assertIn("shop_id", output)


class TestCmdJobs(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def test_jobs_returns_result(self):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"status": "done"}'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_jobs, "123", "shop1", "taobao", "k3")

        self.assertIn("done", output)


class TestCmdPublish(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def test_publish_saves_record(self):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"job-id": 42}'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            output = self._capture_stdout(cmd_publish, "100,200", "shop01", "taobao", "k3")

        self.assertIn("job-id", output)
        # 验证记录文件被创建
        records = [f for f in os.listdir(self.records_dir) if f.endswith(".json")]
        self.assertEqual(len(records), 1)
        with open(os.path.join(self.records_dir, records[0])) as f:
            data = json.load(f)
        self.assertEqual(data["tasks"][0]["product_ids"], "100,200")
        self.assertEqual(data["tasks"][0]["platform"], "k3")
        self.assertEqual(data["tasks"][0]["shop_id"], "shop01")
        self.assertEqual(data["tasks"][0]["shop_type"], "taobao")
        self.assertEqual(data["tasks"][0]["job_id"], "42")

    def test_publish_appends_to_existing_record(self):
        # 先写一条已有记录
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        record_file = os.path.join(self.records_dir, f"{today}.json")
        with open(record_file, "w") as f:
            json.dump({"date": today, "tasks": [
                {"time": "old", "platform": "k3", "product_ids": "1", "shop_id": "s", "shop_type": "t", "job_id": "1", "response": "old"}
            ]}, f)

        mock_resp = unittest.mock.MagicMock()
        mock_resp.__enter__ = unittest.mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"job-id": 99}'
        mock_resp.status = 200

        with unittest.mock.patch("urllib.request.urlopen", return_value=mock_resp):
            self._capture_stdout(cmd_publish, "2", "s2", "jd", "k3")

        with open(record_file) as f:
            data = json.load(f)
        self.assertEqual(len(data["tasks"]), 2)


class TestCmdRecords(BaseTestCase):

    def test_no_records(self):
        output = self._capture_stdout(cmd_records, "2099-01-01")
        self.assertIn("没有 2099-01-01", output)

    def test_show_records(self):
        record_file = os.path.join(self.records_dir, "2099-01-01.json")
        os.makedirs(self.records_dir, exist_ok=True)
        with open(record_file, "w") as f:
            json.dump({"date": "2099-01-01", "tasks": []}, f)

        output = self._capture_stdout(cmd_records, "2099-01-01")
        self.assertIn("2099-01-01", output)


class TestCmdRecordList(BaseTestCase):

    def test_empty_list(self):
        output = self._capture_stdout(cmd_record_list)
        self.assertIn("暂无记录", output)

    def test_lists_files(self):
        os.makedirs(self.records_dir, exist_ok=True)
        with open(os.path.join(self.records_dir, "2026-01-01.json"), "w") as f:
            json.dump({}, f)
        with open(os.path.join(self.records_dir, "2026-01-02.json"), "w") as f:
            json.dump({}, f)

        output = self._capture_stdout(cmd_record_list)
        self.assertIn("2026-01-02.json", output)
        self.assertIn("2026-01-01.json", output)


class TestCmdRecordExport(BaseTestCase):

    def test_empty_export(self):
        # 删除 records_dir 以触发「暂无记录」
        import shutil
        shutil.rmtree(self.records_dir, ignore_errors=True)
        output = self._capture_stdout(cmd_record_export)
        self.assertIn("暂无记录", output)

    def test_export_csv(self):
        os.makedirs(self.records_dir, exist_ok=True)
        with open(os.path.join(self.records_dir, "2026-06-01.json"), "w") as f:
            json.dump({
                "date": "2026-06-01",
                "tasks": [{
                    "time": "2026-06-01T10:00:00+0000",
                    "platform": "k3",
                    "product_ids": "100",
                    "shop_id": "s1",
                    "shop_type": "tb",
                    "job_id": "42",
                }]
            }, f)

        output = self._capture_stdout(cmd_record_export)
        self.assertIn("日期,时间,平台", output)
        self.assertIn("2026-06-01", output)
        self.assertIn("100", output)
        self.assertIn("s1", output)
        self.assertIn("tb", output)
        self.assertIn("42", output)

    def test_export_date_range(self):
        os.makedirs(self.records_dir, exist_ok=True)
        for d in ["2026-05-30", "2026-06-01", "2026-06-02"]:
            with open(os.path.join(self.records_dir, f"{d}.json"), "w") as f:
                json.dump({"date": d, "tasks": [{"time": "t", "platform": "k3", "product_ids": "1", "shop_id": "", "shop_type": "", "job_id": "1"}]}, f)

        output = self._capture_stdout(cmd_record_export, start_date="2026-06-01")
        self.assertNotIn("2026-05-30", output)
        self.assertIn("2026-06-01", output)
        self.assertIn("2026-06-02", output)


class TestCmdSetup(BaseTestCase):

    def test_setup_skips_empty_input(self):
        """输入空行跳过，不报错。"""
        # 模拟: k3 输入空行跳过, bao66 输入空行跳过
        stdin = io.StringIO("\n\n")
        with unittest.mock.patch("sys.stdin", stdin):
            output = self._capture_stdout(cmd_setup)

        self.assertIn("=== 当前配置 ===", output)

    def test_setup_updates_key(self):
        stdin = io.StringIO("sk-new-k3\n\n")  # k3 输入新 key, bao66 跳过
        with unittest.mock.patch("sys.stdin", stdin):
            output = self._capture_stdout(cmd_setup)

        self.assertIn("API-Key 已更新", output)
        self.assertEqual(load_api_key("k3"), "sk-new-k3")


class TestUsage(unittest.TestCase):

    def test_usage_output(self):
        buf = io.StringIO()
        with unittest.mock.patch("sys.stdout", buf):
            usage()
        output = buf.getvalue()
        self.assertIn("setup", output)
        self.assertIn("today", output)
        self.assertIn("search", output)
        self.assertIn("publish", output)
        self.assertIn("k3", output)
        self.assertIn("bao66", output)
        self.assertIn("API-Key", output)
        # v1.1 新增
        self.assertIn("dashboard", output)
        self.assertIn("batch-title", output)
        self.assertIn("title-check", output)
        self.assertIn("update-product", output)



# ── 淘宝 / 快捷命令测试 ────────────────────────────────────

class TestTaobaoDashboard(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def _mock_list(self):
        mock = unittest.mock.MagicMock()
        mock.__enter__ = unittest.mock.MagicMock(return_value=mock)
        mock.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock.read.return_value = b'{"code":0,"msg":"success","data":{"data":{"items":{"item":[{"num_iid":123,"title":"test"}]}}}}'
        mock.status = 200
        return mock

    def test_dashboard_output(self):
        m = self._mock_list()
        with unittest.mock.patch("urllib.request.urlopen", return_value=m):
            output = self._capture_stdout(cmd_taobao_dashboard, "556", "k3")
        self.assertIn("店铺仪表盘", output)


class TestTitleCheck(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._write_config(["API_KEY_k3=sk-test"])

    def _mock_products(self, titles):
        items = [{"num_iid": i, "title": t} for i, t in enumerate(titles)]
        body = json.dumps({"code": 0, "msg": "success", "data": {"data": {"items": {"item": items}}}})
        mock = unittest.mock.MagicMock()
        mock.__enter__ = unittest.mock.MagicMock(return_value=mock)
        mock.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock.read.return_value = body.encode()
        mock.status = 200
        return mock

    def test_short_title_warning(self):
        m = self._mock_products(["AB"])  # 2字符, 太短
        with unittest.mock.patch("urllib.request.urlopen", return_value=m):
            output = self._capture_stdout(cmd_taobao_title_check, "556", "k3")
        self.assertIn("偏短", output)

    def test_no_year_warning(self):
        m = self._mock_products(["时尚凉鞋舒适百搭女鞋春夏新款"])  # 无年份
        with unittest.mock.patch("urllib.request.urlopen", return_value=m):
            output = self._capture_stdout(cmd_taobao_title_check, "556", "k3")
        self.assertIn("缺年份/季节", output)

    def test_good_title_passes(self):
        m = self._mock_products(["2026夏季新款时尚凉鞋女平底舒适百搭"])
        with unittest.mock.patch("urllib.request.urlopen", return_value=m):
            output = self._capture_stdout(cmd_taobao_title_check, "556", "k3")
        self.assertIn("质量良好", output)


class TestConstants(unittest.TestCase):

    def test_base_url(self):
        self.assertEqual(BASE_URL, "http://open.jybc.com.cn/agent")

    def test_platforms(self):
        self.assertIn("k3", PLATFORMS)
        self.assertIn("bao66", PLATFORMS)
        self.assertEqual(PLATFORMS["k3"], "开山网")
        self.assertEqual(PLATFORMS["bao66"], "包牛牛")

    def test_default_platform(self):
        self.assertEqual(DEFAULT_PLATFORM, "k3")


if __name__ == "__main__":
    unittest.main()
