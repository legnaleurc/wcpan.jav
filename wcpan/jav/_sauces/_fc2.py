import re
from typing import override

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name


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


class _Fc2DetailedProduct(DetailedProduct):
    def __init__(self, *, product: Product, title: str) -> None:
        super().__init__()

        self._p = product
        self._title = title

    @property
    @override
    def sauce(self) -> str:
        return self._p.sauce

    @property
    @override
    def id(self) -> str:
        return self._p.id

    @property
    @override
    def url(self) -> str:
        return self._p.url

    @property
    @override
    def title(self) -> str:
        return self._title

    @property
    @override
    def actresses(self) -> list[str]:
        return []


async def _fetch(product: Product) -> DetailedProduct | None:
    soup = await get_html(product.url)
    if not soup:
        return None

    title = soup.select_one('head > meta[name="twitter:title"]')
    if not title:
        return None
    meta = title.attrs.get("content")
    if not meta:
        return None
    if not isinstance(meta, str):
        return None
    name = normalize_name(meta)

    return _Fc2DetailedProduct(product=product, title=name)
