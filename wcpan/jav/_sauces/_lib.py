from contextlib import asynccontextmanager
from typing import Any

from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def get_html(
    url: str,
    *,
    queries: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
) -> BeautifulSoup | None:
    async with _http_get(url, queries=queries, cookies=cookies) as response:
        html = await response.text(errors="ignore")
    return BeautifulSoup(html, "html.parser")


async def get_json(url: str) -> Any:
    async with _http_get(url) as response:
        return await response.json()


@asynccontextmanager
async def _http_get(
    url: str,
    *,
    queries: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
):
    async with (
        ClientSession() as session,
        session.get(url, params=queries, cookies=cookies) as response,
    ):
        response.raise_for_status()
        yield response


def normalize_name(name: str) -> str:
    name = name.strip()
    name = name.replace("/", "／")
    name = name.replace("\n", "")
    name = name.replace("\r", "")
    return name
