import re
from typing import override
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"n(\d{4})", unknown_text, re.I)
    if not m:
        return None

    video_id = m.group(0)
    video_id = video_id.lower()
    return await _fetch(video_id)


async def _fetch(video_id: str) -> Product | None:
    soup = await get_html(
        f"https://www.tokyo-hot.com/product/",
        queries={
            "q": video_id,
        },
    )
    if not soup:
        return None

    anchor = soup.select_one("a.rm")
    if not anchor:
        return None

    href = anchor.attrs.get("href")
    if not href:
        return None
    if not isinstance(href, str):
        return None
    url = urljoin("https://www.tokyo-hot.com", href)

    return _TokyoHotProduct(video_id=video_id, url=url)


class _TokyoHotProduct(Product):
    def __init__(self, *, video_id: str, url: str) -> None:
        super().__init__()

        self._vid = video_id
        self._url = url

    @property
    @override
    def sauce(self) -> str:
        return "tokyohot"

    @property
    @override
    def id(self) -> str:
        return f"Tokyo-Hot {self._vid}"

    @property
    @override
    def url(self) -> str:
        return self._url

    @override
    async def __call__(self) -> DetailedProduct | None:
        return await _fetch_detail(self)


async def _fetch_detail(product: Product) -> DetailedProduct | None:
    soup = await get_html(product.url + "?lang=ja")
    if not soup:
        return None

    title = _get_title(soup)
    if not title:
        return None

    actresses = _get_actresses(soup)
    if not actresses:
        return None

    return SimpleDetailedProduct(product=product, title=title, actresses=actresses)


def _get_title(soup: BeautifulSoup) -> str:
    title = soup.select_one(".pagetitle > h2")
    if not title:
        return ""
    title = title.get_text()
    return normalize_name(title)


def _get_actresses(soup: BeautifulSoup) -> list[str]:
    actor = soup.select_one(".info > dd:nth-child(2) > a:nth-child(1)")
    if not actor:
        return []
    actor = actor.get_text()
    actor = normalize_name(actor)
    return [actor]
