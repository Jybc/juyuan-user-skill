# K3 平台 API 参考

## 基础信息

- Base URL: `https://open.jybc.com.cn/agent`
- 认证: URL 查询参数 `api_key=<your-api-key>`
- **User-Agent**: `juyuan-skill/1.0`
- **不同平台的 API Key 独立，互不通用**，需分别在平台后台获取
- 默认平台: `k3`（开山网）
- 可选平台: `bao66`（包牛牛）
- 响应格式: JSON
- 所有接口默认 `platform=k3`，除非用户明确修改平台

## 接口列表

### 1. 获取今日新款列表

```
GET /product/today?page={page}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1，每页 20 条 |

返回字段含 `index_image`（商品主图 URL）。

默认 `platform=k3`，可通过 `?platform=bao66` 切到包牛牛。

### 2. 搜索产品

```
GET /product/search?wd={keyword}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| wd | string | 是 | 搜索关键词（需 URL 编码） |

每次最多返回 20 个产品。默认 `platform=k3`。

### 3. 获取店铺列表

```
GET /user/shops
```

无需参数。返回用户在当前平台下已绑定的店铺列表，包含 `shop_id` 和 `shop_type`。

默认 `platform=k3`。

### 4. 提交极速发布任务

```
POST /product/fast-publish
Content-Type: application/x-www-form-urlencoded
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 是 | k3 或 bao66 |
| product_id | string | 是 | 产品 ID |
| shop_id | string | 是 | 店铺 ID（通过 `/user/shops` 获取） |
| shop_type | string | 是 | 店铺类型（通过 `/user/shops` 获取） |

### 5. 查看发布任务结果

```
GET /product/fast-publish-result
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 是 | k3 或 bao66 |
| product_id | string | 是 | 产品 ID |
| shop_id | string | 是 | 店铺 ID |
| shop_type | string | 是 | 店铺类型 |
