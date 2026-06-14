import json
import re
from datetime import datetime
from typing import override

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name
from ._types import SimpleDetailedProduct


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"HEYZO[-_](\d{4})", unknown_text, re.I)
    if not m:
        return None
    number = m.group(1)
    return _HeyzoProduct(number=number)


class _HeyzoProduct(Product):
    def __init__(self, *, number: str) -> None:
        super().__init__()

        self._number = number

    @property
    @override
    def sauce(self) -> str:
        return "heyzo"

    @property
    @override
    def id(self) -> str:
        return f"HEYZO-{self._number}"

    @property
    @override
    def url(self) -> str:
        return f"https://www.heyzo.com/moviepages/{self._number}/index.html"

    @override
    async def __call__(self) -> DetailedProduct | None:
        return await _fetch(self)


async def _fetch(product: Product) -> DetailedProduct | None:
    soup = await get_html(product.url)
    if not soup:
        return None

    json_ld = soup.select_one('script[type="application/ld+json"]')
    if not json_ld:
        return None

    json_ld = json.loads(json_ld.get_text())
    video = json_ld.get("video", {})

    title = video.get("name", "")
    if not title:
        return None
    title = normalize_name(title)

    actresses = [normalize_name(video["actor"]) if "actor" in video else ""]

    released_at = (
        datetime.fromisoformat(video["uploadDate"]).date()
        if "uploadDate" in video
        else None
    )

    return SimpleDetailedProduct(
        product=product, title=title, actresses=actresses, released_at=released_at
    )
