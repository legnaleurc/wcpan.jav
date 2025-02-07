import re
from typing import override

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

    title = soup.select_one(".movie-info .heading")
    if not title:
        return None
    title = normalize_name(title.get_text())

    actresses = []
    actor = soup.select_one(".movie-spec .spec-content > .spec-item")
    if actor:
        actor = normalize_name(actor.get_text())
        actresses = [actor]

    return SimpleDetailedProduct(product=product, title=title, actresses=actresses)
