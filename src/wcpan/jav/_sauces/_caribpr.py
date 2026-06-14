import re
from datetime import date
from typing import override

from bs4 import BeautifulSoup

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"(\d{6})[-_](\d{3})-CARIBPR", unknown_text, re.I)
    if not m:
        return None

    series = m.group(1)
    number = m.group(2)
    return _CaribprProduct(series=series, number=number)


class _CaribprProduct(Product):
    def __init__(self, *, series: str, number: str) -> None:
        super().__init__()

        self._series = series
        self._number = number

    @property
    @override
    def sauce(self) -> str:
        return "caribpr"

    @property
    @override
    def id(self) -> str:
        return f"{self._series}-{self._number}-CARIBPR"

    @property
    @override
    def url(self) -> str:
        return f"https://www.caribbeancompr.com/moviepages/{self._series}-{self._number}/index.html"

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
    title = soup.select_one(".movie-info .heading")
    if not title:
        return ""

    return normalize_name(title.get_text())


def _get_actresses(soup: BeautifulSoup) -> list[str]:
    actor = soup.select_one(".movie-spec .spec-content > .spec-item")
    if not actor:
        return []

    actor_name = normalize_name(actor.get_text())
    return [actor_name]


def _get_released_at(soup: BeautifulSoup) -> date | None:
    upload_date = soup.select_one(".spec-content[itemprop=datePublished]")
    if not upload_date:
        return None

    released_at = upload_date.get_text().strip().replace("/", "-")
    return date.fromisoformat(released_at)
