import re
from typing import override

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"(\d{3,4}\w{3,6})[-_](\d{3,4}\w?)", unknown_text)
    if not m:
        return None

    video_id = _VideoId(m.group(1), m.group(2))
    return _MgstageProduct(video_id=video_id)


class _VideoId:
    def __init__(self, series: str, number: str) -> None:
        self._series = series.upper()
        self._number = number
        self._re = re.compile(rf"{self._series}.*{self._number}", re.I)

    @property
    def series(self) -> str:
        return self._series

    @property
    def number(self) -> str:
        return self._number

    def __str__(self) -> str:
        return f"{self.series}-{self.number}"


class _MgstageProduct(Product):
    def __init__(self, *, video_id: _VideoId) -> None:
        super().__init__()

        self._vid = video_id

    @property
    @override
    def sauce(self) -> str:
        return "mgstage"

    @property
    @override
    def id(self) -> str:
        return str(self._vid)

    @property
    @override
    def url(self) -> str:
        return f"https://www.mgstage.com/product/product_detail/{self.id}/"

    @override
    async def __call__(self) -> DetailedProduct | None:
        return await _fetch(self, self._vid)


async def _fetch(product: Product, video_id: _VideoId) -> DetailedProduct | None:
    soup = await get_html(
        product.url,
        cookies={
            "adc": "1",
        },
    )
    if not soup:
        return None

    title = soup.select_one(".tag")
    if not title:
        return None

    title = normalize_name(title.get_text())

    return SimpleDetailedProduct(product=product, title=title, actresses=[])
