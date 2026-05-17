# SearXNG Search Plugin

MaiBot 搜索插件，通过调用本地 [SearXNG](https://docs.searxng.org/) 实例实现网页搜索。

## 功能

- 支持通用网页、新闻、图片、音乐、文件、学术、IT、社交媒体、地图等多种搜索类别（通过配置开关控制）
- 搜索结果自动注入 Replyer 上下文，让 LLM 回复时可以参考搜索结果
- 支持"始终可见"和"按需发现"两种工具模式
- 支持 JSON 和纯文本两种结果格式

## 部署 SearXNG

推荐使用 Docker 部署：

```bash
# 拉取镜像
docker pull searxng/searxng

# 创建配置目录
mkdir -p /opt/searxng
cd /opt/searxng

# 生成默认配置文件
docker run --rm searxng/searxng cat /etc/searxng/settings.yml > settings.yml
docker run --rm searxng/searxng cat /etc/searxng/limiter.toml > limiter.toml
docker run --rm searxng/searxng cat /etc/searxng/uwsgi.ini > uwsgi.ini

# 编辑 settings.yml，将 secret_key 改为随机字符串，关闭表单搜索
# settings.yml:
#   search:
#     formats: [html, json]   # 确保 json 格式开启
#   server:
#     secret_key: "<随机字符串>"
#     bind_address: "0.0.0.0"
#     limiter: false
#     public_instance: false
#   ui:
#     static_use_hash: true

# 启动容器
docker run -d \
  --name searxng \
  -p 8888:8080 \
  -v /opt/searxng/settings.yml:/etc/searxng/settings.yml:ro \
  -v /opt/searxng/limiter.toml:/etc/searxng/limiter.toml:ro \
  -v /opt/searxng/uwsgi.ini:/etc/searxng/uwsgi.ini:ro \
  searxng/searxng
```

部署完成后访问 `http://<服务器IP>:8888` 验证 SearXNG 是否正常运行。

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
