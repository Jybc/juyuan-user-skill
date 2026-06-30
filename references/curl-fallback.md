# curl 降级方案

当环境中没有 Python 时，用 curl 直接调用所有 API。

## 前置条件

`~/.config/k3-publish/config` 中需配置 API Key。**不同平台（k3/bao66）的 Key 独立，互不通用。**

获取 API Key：在各平台后台获取后，手动写入 config：
```
API_KEY_k3=你的开山网Key
API_KEY_bao66=你的包牛牛Key
```

或通过 python 驱动设置：`python scripts/driver.py setup`。

## 各接口 curl 示例

### 获取今日新款

```bash
curl -s -H "User-Agent: juyuan-skill/1.0" \
  "https://open.jybc.com.cn/agent/product/today?page=1&platform=k3&api_key=<你的key>"
```

### 搜索产品

```bash
curl -s -H "User-Agent: juyuan-skill/1.0" \
  "https://open.jybc.com.cn/agent/product/search?wd=关键词&platform=k3&api_key=<你的key>"
```

### 获取店铺列表

```bash
curl -s -H "User-Agent: juyuan-skill/1.0" \
  "https://open.jybc.com.cn/agent/user/shops?platform=k3&api_key=<你的key>"
```

返回的 JSON 中找到 `shop_id` 和 `shop_type`，用于后续发布。

### 提交极速发布

```bash
curl -s -X POST -H "User-Agent: juyuan-skill/1.0" \
  -d "platform=k3&api_key=<你的key>&product_id=产品ID&shop_id=店铺ID&shop_type=店铺类型" \
  "https://open.jybc.com.cn/agent/product/fast-publish"
```

### 查看发布任务结果

```bash
curl -s -H "User-Agent: juyuan-skill/1.0" \
  "https://open.jybc.com.cn/agent/product/fast-publish-result?platform=k3&product_id=产品ID&shop_id=店铺ID&shop_type=店铺类型&api_key=<你的key>"
```

## 平台切换

所有接口默认 `platform=k3`，改为 `platform=bao66` 即切到包牛牛。

## curl 环境检查

```bash
curl --version > /dev/null 2>&1 && echo "OK" || echo "curl 不可用"
```
