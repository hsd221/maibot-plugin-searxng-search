"""SearXNG API 客户端。"""

from __future__ import annotations

from dataclasses import dataclass

import aiohttp


def _make_search_result(item: dict) -> SearchResult:
    return SearchResult(
        url=item.get("url") or "",
        title=item.get("title") or "",
        content=item.get("content") or "",
        engine=item.get("engine") or "",
        score=float(item.get("score") or 0),
    )


def _make_image_result(item: dict) -> ImageResult:
    return ImageResult(
        img_src=item.get("img_src") or "",
        thumbnail_src=item.get("thumbnail_src") or item.get("thumbnail") or "",
        title=item.get("title") or "",
        url=item.get("url") or "",
        source=item.get("source") or item.get("engine") or "",
    )


@dataclass
class SearchResult:
    """网页搜索结果。"""

    url: str
    title: str = ""
    content: str = ""
    engine: str = ""
    score: float = 0.0


@dataclass
class ImageResult:
    """图片搜索结果。"""

    img_src: str
    thumbnail_src: str = ""
    title: str = ""
    url: str = ""
    source: str = ""


class SearXNGClient:
    """SearXNG 搜索 API 客户端。

    Args:
        host: SearXNG 实例地址，默认 ``"http://localhost"``。
        port: 端口号，默认 ``8888``。
        timeout: 请求超时秒数，默认 ``10.0``。
    """

    def __init__(
        self,
        host: str = "http://localhost",
        port: int = 8888,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = f"{host.rstrip('/')}:{port}"
        self.timeout = timeout

    async def _request(self, params: dict) -> dict:
        url = f"{self.base_url}/search"
        client_timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _fetch(
        self,
        query: str,
        params: dict,
        factory: callable,
        max_results: int,
    ) -> list:
        params.update({"q": query, "format": "json"})
        data = await self._request(params)
        return [factory(item) for item in data.get("results", [])[:max_results]]

    async def search(
        self,
        query: str,
        categories: list[str] | None = None,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """执行网页搜索。参数 *categories* 为类别列表（如 ``["general", "news"]``），
        不传则使用 SearXNG 默认类别。"""
        params: dict = {}
        if categories:
            params["categories"] = ",".join(categories)
        return await self._fetch(query, params, _make_search_result, max_results)

    async def search_images(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[ImageResult]:
        """执行图片搜索。"""
        return await self._fetch(query, {"categories": "images"}, _make_image_result, max_results)
