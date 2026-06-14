import re
from datetime import date
from typing import override

from bs4 import BeautifulSoup

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"fc2[-_]ppv[-_](\d+)", unknown_text, re.I)
    if not m:
        return None

    video_id = m.group(1)
    return _Fc2Product(video_id=video_id)


class _Fc2Product(Product):
    def __init__(self, *, video_id: str) -> None:
        super().__init__()

        self._vid = video_id

    @property
    @override
    def sauce(self) -> str:
        return "fc2"

    @property
    @override
    def id(self) -> str:
        return f"FC2-PPV-{self._vid}"

    @property
    @override
    def url(self) -> str:
        return f"https://adult.contents.fc2.com/article/{self._vid}/"

    @override
    async def __call__(self) -> DetailedProduct | None:
        return await _fetch(self)


async def _fetch(product: Product) -> DetailedProduct | None:
    soup = await get_html(product.url)
    if not soup:
        return None

    name = _get_title(soup)
    if not name:
        return None

    released_at = _get_released_at(soup)

    return SimpleDetailedProduct(
        product=product, title=name, actresses=[], released_at=released_at
    )


def _get_title(soup: BeautifulSoup) -> str:
    title = soup.select_one('head > meta[name="twitter:title"]')
    if not title:
        return ""

    meta = title.attrs.get("content")
    if not meta:
        return ""
    if not isinstance(meta, str):
        return ""

    return normalize_name(meta)


def _get_released_at(soup: BeautifulSoup) -> date | None:
    sale_day = soup.select_one(
        "div.items_article_softDevice:nth-child(5) > p:nth-child(1)"
    )
    if not sale_day:
        return None

    sale_day = sale_day.get_text().strip()[-10:]
    sale_day = sale_day.replace("/", "-")
    return date.fromisoformat(sale_day)
