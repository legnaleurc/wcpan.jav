import re
from typing import override

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

    title = soup.select_one("#title-bg > h1")
    if not title:
        return None

    for span in title.find_all("span"):
        span.decompose()

    title = title.get_text()
    title = normalize_name(title)
    return SimpleDetailedProduct(product=product, title=title, actresses=[])
