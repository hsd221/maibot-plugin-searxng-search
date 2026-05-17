"""SearXNG 搜索插件。"""

from __future__ import annotations

from typing import Any, ClassVar

from maibot_sdk import HookHandler, MaiBotPlugin, PluginConfigBase, Tool
from maibot_sdk.types import HookMode, ToolParameterInfo, ToolParamType

from plugins.searxng_search.config import SearXNGSearchConfig
from plugins.searxng_search.searxng_client import SearXNGClient, SearchResult


def format_search_results(
    results: list[SearchResult],
    result_format: str,
) -> list[dict[str, Any]] | str:
    """将搜索结果格式化为指定格式。

    Args:
        results: SearchResult 列表。
        result_format: ``"json"`` 或 ``"text"``。

    Returns:
        JSON 模式返回字典列表，text 模式返回格式化字符串。
    """
    if not results:
        if result_format == "text":
            return "未找到相关结果。"
        return [{"title": "未找到相关结果", "url": "", "content": "", "engine": "", "score": 0}]

    if result_format == "text":
        blocks: list[str] = []
        for i, r in enumerate(results, 1):
            blocks.append(f"{i}. **{r.title}**\n   {r.content}\n   {r.url}")
        return "\n\n".join(blocks)

    return [
        {
            "url": r.url,
            "title": r.title,
            "content": r.content,
            "engine": r.engine,
            "score": r.score,
        }
        for r in results
    ]


class SearXNGSearchPlugin(MaiBotPlugin):
    """SearXNG 搜索插件。

    通过 planner 工具调用本地 SearXNG 实例执行网页/新闻/图片搜索。
    """

    config_model: ClassVar[type[PluginConfigBase] | None] = SearXNGSearchConfig

    @classmethod
    def build_config_schema(
        cls,
        *,
        plugin_id: str = "",
        plugin_name: str = "",
        plugin_version: str = "",
        plugin_description: str = "",
        plugin_author: str = "",
    ) -> dict[str, Any]:
        schema = super().build_config_schema(
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            plugin_version=plugin_version,
            plugin_description=plugin_description,
            plugin_author=plugin_author,
        )
        schema.get("sections", {}).pop("plugin", None)
        return schema

    def get_components(self) -> list[dict[str, Any]]:
        components = super().get_components()
        for comp in components:
            inner = comp.get("metadata", {}).get("metadata")
            if isinstance(inner, dict) and "core_tool" in inner:
                comp["metadata"]["core_tool"] = inner["core_tool"]
        return components

    # ─── 生命周期 ────────────────────────────────────────────

    async def on_load(self) -> None:
        self._last_search_content: str = ""
        self.ctx.logger.info("[SearXNGSearch] 插件已加载")

    async def on_unload(self) -> None:
        self.ctx.logger.info("[SearXNGSearch] 插件已卸载")

    async def on_config_update(
        self, scope: str, config_data: dict[str, Any], version: str
    ) -> None:
        if scope == "self":
            self.set_plugin_config(config_data)

    # ─── Tool: search_web ────────────────────────────────────

    @Tool(
        name="search_web",
        description="通过 SearXNG 搜索引擎搜索网页。返回结果的标题、URL、内容摘要和来源引擎。",
        parameters=[
            ToolParameterInfo(
                name="query",
                param_type=ToolParamType.STRING,
                description="搜索关键词",
                required=True,
            ),
        ],
        core_tool=True,
    )
    async def handle_search_web(
        self,
        query: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        del kwargs

        if not self.config.plugin.enabled:
            return {"success": False, "error": "搜索插件未启用"}

        if not query.strip():
            return {"success": False, "error": "搜索关键词不能为空"}

        cfg = self.config.searxng
        category_list = cfg.get_enabled_categories()

        client = SearXNGClient(
            host=cfg.host,
            port=cfg.port,
            timeout=cfg.request_timeout,
        )

        results = await client.search(
            query=query, categories=category_list, max_results=cfg.max_results,
        )

        formatted = format_search_results(results, cfg.result_format)

        # 以纯文本格式存储，供 replyer 注入使用
        text_version = format_search_results(results, "text")
        self._last_search_content = text_version if isinstance(text_version, str) else str(text_version)

        return {
            "success": True,
            "content": formatted,
            "query": query,
            "categories": category_list,
            "result_count": len(results),
        }

    # ─── Hook: 将搜索结果注入 replyer 上下文 ─────────────────

    @HookHandler(
        "maisaka.planner.after_response",
        mode=HookMode.BLOCKING,
    )
    async def inject_search_into_reply_reference(self, **kwargs: Any) -> dict[str, Any]:
        """在 planner 决定调用 reply 时，将最近一次搜索结果注入 reference_info。"""
        if not self._last_search_content:
            return {"modified_kwargs": kwargs}

        tool_calls = kwargs.get("tool_calls")
        if not isinstance(tool_calls, list):
            return {"modified_kwargs": kwargs}

        search_content = self._last_search_content
        self._last_search_content = ""

        for tc in tool_calls:
            if not isinstance(tc, dict):
                continue
            func = tc.get("function", {})
            if not isinstance(func, dict):
                continue
            if func.get("name") != "reply":
                continue
            args = func.get("arguments", {})
            if not isinstance(args, dict):
                continue
            existing = str(args.get("reference_info", "") or "").strip()
            injection = f"[搜索: {search_content}]"
            args["reference_info"] = f"{existing}\n{injection}" if existing else injection
            func["arguments"] = args
            tc["function"] = func
            self.ctx.logger.debug("[SearXNGSearch] 搜索结果注入到 reply reference_info")
            break

        return {"modified_kwargs": kwargs}

    # ─── Hook: tool_mode 控制工具可见性 ─────────────────────

    @HookHandler(
        "maisaka.planner.before_request",
        mode=HookMode.BLOCKING,
    )
    async def filter_search_web_tool_mode(self, **kwargs: Any) -> dict[str, Any]:
        """当 tool_mode 配置为 ``"按需发现"`` 时，从 planner 工具列表中移除 search_web。"""
        if self.config.searxng.tool_mode != "按需发现":
            return {"modified_kwargs": kwargs}
        tools = kwargs.get("tool_definitions")
        if isinstance(tools, list):
            before = len(tools)
            kwargs["tool_definitions"] = [
                t for t in tools
                if not (
                    isinstance(t, dict)
                    and t.get("function", {}).get("name") == "search_web"
                )
            ]
            after = len(kwargs["tool_definitions"])
            self.ctx.logger.debug(
                f"[SearXNGSearch] tool_mode=按需发现: "
                f"{before} → {after} tools (removed search_web)"
            )
        return {"modified_kwargs": kwargs}

def create_plugin() -> SearXNGSearchPlugin:
    return SearXNGSearchPlugin()
