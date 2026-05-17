"""SearXNG 搜索插件配置模型。"""

from __future__ import annotations

from typing import Literal

from maibot_sdk import PluginConfigBase
from pydantic import Field


class PluginSectionConfig(PluginConfigBase):
    """插件基础配置。"""

    enabled: bool = Field(default=True)
    config_version: str = Field(default="1.0.0")


class SearXNGSectionConfig(PluginConfigBase):
    """SearXNG 连接与搜索行为配置。"""

    __ui_label__ = "SearXNG 搜索"
    __ui_icon__ = "Search"

    host: str = Field(
        default="http://localhost",
        description="SearXNG 实例地址",
        json_schema_extra={"label": "主机地址", "placeholder": "http://localhost"},
    )
    port: int = Field(
        default=8888,
        description="SearXNG 端口号",
        json_schema_extra={"label": "端口"},
    )
    search_general: bool = Field(
        default=True,
        description="通用网页搜索",
        json_schema_extra={"label": "通用网页"},
    )
    search_news: bool = Field(
        default=True,
        description="新闻搜索",
        json_schema_extra={"label": "新闻"},
    )
    search_images: bool = Field(
        default=False,
        description="图片搜索",
        json_schema_extra={"label": "图片"},
    )
    search_music: bool = Field(
        default=False,
        description="音乐搜索",
        json_schema_extra={"label": "音乐"},
    )
    search_files: bool = Field(
        default=False,
        description="文件搜索",
        json_schema_extra={"label": "文件"},
    )
    search_science: bool = Field(
        default=False,
        description="学术搜索",
        json_schema_extra={"label": "学术"},
    )
    search_it: bool = Field(
        default=False,
        description="IT 技术搜索",
        json_schema_extra={"label": "IT 技术"},
    )
    search_social_media: bool = Field(
        default=False,
        description="社交媒体搜索",
        json_schema_extra={"label": "社交媒体"},
    )
    search_map: bool = Field(
        default=False,
        description="地图搜索",
        json_schema_extra={"label": "地图"},
    )
    result_format: Literal["json", "text"] = Field(
        default="json",
        description="结果返回格式",
        json_schema_extra={"label": "结果格式"},
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="单次搜索最大返回条数",
        json_schema_extra={"label": "最大结果数"},
    )
    tool_mode: Literal["始终可见", "按需发现"] = Field(
        default="始终可见",
        description="始终可见：每次对话都提供搜索工具；按需发现：LLM 需要时自行搜索该工具",
        json_schema_extra={"label": "工具模式"},
    )
    request_timeout: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="SearXNG 请求超时秒数",
        json_schema_extra={"label": "请求超时"},
    )

    def get_enabled_categories(self) -> list[str]:
        """返回当前启用的搜索类别列表。"""
        _CATEGORY_MAP: dict[str, str] = {
            "search_general": "general",
            "search_news": "news",
            "search_images": "images",
            "search_music": "music",
            "search_files": "files",
            "search_science": "science",
            "search_it": "it",
            "search_social_media": "social media",
            "search_map": "map",
        }
        return [
            api_name
            for field_name, api_name in _CATEGORY_MAP.items()
            if getattr(self, field_name, False)
        ]


class SearXNGSearchConfig(PluginConfigBase):
    """SearXNG 搜索插件配置。"""

    __ui_label__ = "SearXNG 搜索"

    plugin: PluginSectionConfig = Field(
        default_factory=PluginSectionConfig,
    )
    searxng: SearXNGSectionConfig = Field(
        default_factory=SearXNGSectionConfig,
    )
