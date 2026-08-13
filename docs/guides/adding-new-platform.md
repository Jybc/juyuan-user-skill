# 新平台接入指南

将新的电商平台（如抖音、PDD）接入「聚源百成大师」Skill 的标准流程。

---

## 接入步骤概览

```
1. jybc 后端 → 添加平台路由（如 /douyin/*）
2. 聚源百成MCP → 开发平台 MCP Tool
3. juyuan-user-skill → 创建平台 ops 模块 + Agent prompts + API 文档
4. SKILL.md → 路由表追加一行
```

---

## 第 1 步: jybc 后端添加路由

在 `open.jybc.com.cn` Laravel 项目中添加平台路由映射。

**文件**: `routes/agent.php`

```php
// 示例: 添加抖音平台路由
Route::prefix('douyin')->group(function () {
    Route::get('shop/info', 'DouyinController@shopInfo');
    Route::get('product/list', 'DouyinController@productList');
    // ... 按淘宝模式复制所需的 CRUD 接口
});
```

**验证**: `GET /agent/douyin/shop/info?shop_id=xxx`

---

## 第 2 步: 聚源百成MCP 开发 MCP Tool

在 `聚源百成MCP` 项目中，参考淘宝 Tool 模式创建新平台的 Tool。

### 创建目录

```bash
mkdir -p 聚源百成MCP/src/Tools/Douyin
mkdir -p 聚源百成MCP/tests/Tools/Douyin
```

### Tool 实现模板

参考 `src/Tools/Taobao/Shop/ShopInfoTool.php`：

```php
<?php
namespace JuyuanMcp\Tools\Douyin;

use Mcp\Capability\Attribute\McpTool;
use Mcp\Capability\Attribute\Schema;
use JuyuanMcp\JuyuanApiClient;

class ShopInfoTool
{
    public function __construct(private JuyuanApiClient $apiClient) {}

    #[McpTool(
        name: 'douyin_shop_info',
        description: '获取抖音店铺基本信息。shop_id 通过 get_shops 获取。'
    )]
    public function get(
        #[Schema(description: '店铺 ID')] string $shopId
    ): array {
        return $this->apiClient->get('/douyin/shop/info', ['shop_id' => $shopId]);
    }
}
```

### 注册到 ServerFactory

```php
// src/ServerFactory.php
->addTool([\JuyuanMcp\Tools\Douyin\ShopInfoTool::class, 'get'], 'douyin_shop_info')
```

---

## 第 3 步: juyuan-user-skill 创建模块文件

### 3a. 创建 `modules/douyin-ops.md`

```markdown
# 抖音店铺运营模块 (douyin-ops)

> **归属**: SKILL.md → 功能路由表 → `modules/douyin-ops.md`
> **功能**: 商品管理 / 订单管理 / 售后管理 / AI 运营

## 触发词路由

| 功能 | 触发词 | 跳转 |
|------|--------|------|
| 商品管理 | 抖音商品、上下架 | #商品管理 |
| 订单管理 | 抖音订单、发货 | #订单管理 |
| ... | ... | ... |

## MCP Tools（优先使用）

| 操作 | MCP Tool | 降级方案 |
|------|----------|----------|
| 店铺信息 | `douyin_shop_info(shopId)` | `driver.py douyin shop-info` |
| ... | ... | ... |

## 依赖
- SubAgent: `agents/douyin/*.md`
- 参考文档: `references/douyin/*.md`
```

### 3b. 创建 `agents/douyin/` 目录

```bash
mkdir -p juyuan-user-skill/agents/douyin
```

每个 AI 能力的 SubAgent prompt 独立维护。抖音的 SEO 规则、文案风格与淘宝不同，prompt 需基于抖音平台规范编写。

### 3c. 创建 `references/douyin/` 目录

```bash
mkdir -p juyuan-user-skill/references/douyin
```

每个 API 端点一个 `.md` 文件，格式参考 `references/taobao/`。

---

## 第 4 步: SKILL.md 路由表追加

```markdown
| 抖音店铺运营 | 抖音商品、抖音订单、抖音售后、抖音AI | `modules/douyin-ops.md` |
```

---

## 接入检查清单

- [ ] jybc 后端路由已添加
- [ ] 聚源百成MCP Tool 已开发 + 注册 + 测试
- [ ] `modules/<platform>-ops.md` 已创建
- [ ] `agents/<platform>/` 已有至少 1 个 prompt 文件
- [ ] `references/<platform>/` 已有至少 1 个 API 文档
- [ ] `SKILL.md` 路由表已追加一行
- [ ] 端到端验证：搜索 → 发布 → 店铺管理 → AI 运营
