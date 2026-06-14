import re
from datetime import date
from typing import override

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement

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
        return await _fetch(self)


async def _fetch(product: Product) -> DetailedProduct | None:
    soup = await get_html(
        product.url,
        cookies={
            "adc": "1",
        },
    )
    if not soup:
        return None

    title = _get_title(soup)
    if not title:
        return None

    table = _build_table(soup)

    actresses = _get_actresses(table)

    released_at = _get_released_at(table)

    return SimpleDetailedProduct(
        product=product, title=title, actresses=actresses, released_at=released_at
    )


def _get_title(soup: BeautifulSoup) -> str:
    title = soup.select_one(".tag")
    if not title:
        return ""

    return normalize_name(title.get_text())


def _get_actresses(table: dict[str, Tag | PageElement | NavigableString]) -> list[str]:
    actresses = table.get("出演：")
    if actresses is None:
        return []

    if not isinstance(actresses, Tag):
        return []

    anchors = actresses.select("a")
    if anchors:
        return [normalize_name(_.get_text()) for _ in anchors]

    return [normalize_name(actresses.get_text())]


def _get_released_at(
    table: dict[str, Tag | PageElement | NavigableString],
) -> date | None:
    publish_date = table.get("配信開始日：")
    if publish_date is None:
        return None

    publish_date = publish_date.get_text().strip().replace("/", "-")
    return date.fromisoformat(publish_date)


def _build_table(soup: BeautifulSoup) -> dict[str, Tag | PageElement | NavigableString]:
    table: dict[str, Tag | PageElement | NavigableString] = {}
    for row in soup.select(".detail_left table tr"):
        label = row.find("th", recursive=False)
        value = row.find("td", recursive=False)
        if label is None or value is None:
            continue
        table[normalize_name(label.get_text())] = value
    return table
