# SearXNG Search Plugin

MaiBot 搜索插件，通过调用本地 [SearXNG](https://docs.searxng.org/) 实例实现网页搜索。

## 功能

- 支持通用网页、新闻、图片、音乐、文件、学术、IT、社交媒体、地图等多种搜索类别（通过配置开关控制）
- 搜索结果自动注入 Replyer 上下文，让 LLM 回复时可以参考搜索结果
- 支持"始终可见"和"按需发现"两种工具模式
- 支持 JSON 和纯文本两种结果格式

## 部署 SearXNG（Docker Compose 一键部署）

插件仓库自带 SearXNG 配置文件和 docker-compose.yml，复制即可使用：

```bash
# 克隆插件仓库
git clone https://github.com/hsd221/maibot-plugin-searxng-search.git
cd maibot-plugin-searxng-search

# 修改 SearXNG 密钥（务必改为随机字符串）
# Linux/macOS: sed -i 's/change-me-to-a-random-string/$(openssl rand -hex 32)/' searxng/settings.yml

# 启动 SearXNG
docker compose up -d
```

部署完成后访问 `http://<服务器IP>:8888` 验证 SearXNG 是否正常运行。

> 配置文件位于仓库 `searxng/` 目录下：`settings.yml`（搜索引擎配置）、`limiter.toml`（限流配置）、`uwsgi.ini`（uWSGI 配置）。可按需调整。

## 安装插件

### 通过插件商店（推荐）

在 MaiBot WebUI 的插件商店中搜索 `hsd221.searxng-search`，一键安装。

### 手动安装

```bash
# 进入插件目录
cd MaiBot/plugins

# 克隆插件仓库
git clone https://github.com/hsd221/maibot-plugin-searxng-search.git searxng_search
```

## 配置

插件安装后在 MaiBot WebUI 的"插件配置"页面进行配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 主机地址 | SearXNG 实例地址 | `http://localhost` |
| 端口 | SearXNG 端口 | `8888` |
| 通用网页 | 启用通用网页搜索 | 开启 |
| 新闻 | 启用新闻搜索 | 开启 |
| 图片 | 启用图片搜索 | 关闭 |
| 音乐/文件/学术/IT/社交媒体/地图 | 各分类搜索开关 | 关闭 |
| 结果格式 | json 或 text | `json` |
| 最大结果数 | 单次搜索返回条数 (1-20) | `5` |
| 工具模式 | 始终可见 / 按需发现 | `始终可见` |
| 请求超时 | 请求 SearXNG 的超时秒数 | `10.0` |

## 使用

配置完成并启用插件后，LLM 会通过 `search_web` 工具自动调用搜索功能。在对话中直接询问需要搜索的内容即可，插件会自动返回搜索结果供 LLM 参考。
