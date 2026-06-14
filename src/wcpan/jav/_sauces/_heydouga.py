import re
from datetime import date
from typing import override

from bs4 import BeautifulSoup

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknwon_text: str) -> Product | None:
    m = re.search(r"hey(douga)?[-_ ]?(\d+)[-_](\d+)", unknwon_text, re.I)
    if not m:
        return None

    series = m.group(2)
    number = m.group(3)
    return _HeydougaProduct(series=series, number=number)


class _HeydougaProduct(Product):
    def __init__(self, *, series: str, number: str) -> None:
        super().__init__()

        self._series = series
        self._number = number

    @property
    @override
    def sauce(self) -> str:
        return "heydouga"

    @property
    @override
    def id(self) -> str:
        return f"HEYDOUGA-{self._series}-{self._number}"

    @property
    @override
    def url(self) -> str:
        return f"https://www.heydouga.com/moviepages/{self._series}/{self._number}/index.html"

    @override
    async def __call__(self) -> DetailedProduct | None:
        return await _fetch(self)


async def _fetch(product: Product) -> DetailedProduct | None:
    soup = await get_html(product.url)
    if not soup:
        return None

    title = _get_title(soup)
    if not title:
        return None

    actresses = _get_actresses(soup)

    released_at = _get_released_at(soup)

    return SimpleDetailedProduct(
        product=product, title=title, actresses=actresses, released_at=released_at
    )


def _get_title(soup: BeautifulSoup) -> str:
    title = soup.select_one("#title-bg > h1")
    if not title:
        return ""

    for badge in title.select("span,div"):
        badge.decompose()

    title = title.get_text()
    return normalize_name(title)


def _get_actresses(soup: BeautifulSoup) -> list[str]:
    actresses = soup.select_one(
        "#movie-info > ul:nth-child(1) > li:nth-child(2) > span:nth-child(2) > a:nth-child(1)"
    )
    if not actresses:
        return []

    actresses = actresses.get_text()
    return [normalize_name(actresses)]


def _get_released_at(soup: BeautifulSoup) -> date | None:
    publish_date = soup.select_one("li.mb-2 > span:nth-child(2)")
    if not publish_date:
        return None

    publish_date = publish_date.get_text().strip()
    return date.fromisoformat(publish_date)
