import re
from typing import override

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_json, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"(\d{6})[-_](\d{2})-10MU", unknown_text, re.I)
    if not m:
        return None

    series = m.group(1)
    number = m.group(2)
    return _10musumeProduct(series=series, number=number)


class _10musumeProduct(Product):
    def __init__(self, *, series: str, number: str) -> None:
        super().__init__()

        self._query = f"{series}_{number}"

    @property
    @override
    def sauce(self) -> str:
        return "10musume"

    @property
    @override
    def id(self) -> str:
        return f"{self._query}-10MU"

    @property
    @override
    def url(self) -> str:
        return f"https://www.10musume.com/movies/{self._query}/"

    @override
    async def __call__(self) -> DetailedProduct | None:
        return await _fetch(self, self._query)


async def _fetch(product: Product, query: str) -> DetailedProduct | None:
    data = await get_json(
        f"https://www.10musume.com/dyn/phpauto/movie_details/movie_id/{query}.json",
    )
    if not data:
        return None

    title = normalize_name(data["Title"])
    actor = normalize_name(data["Actor"])

    return SimpleDetailedProduct(product=product, title=title, actresses=[actor])
