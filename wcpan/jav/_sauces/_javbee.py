import re
from typing import override

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"fc2[-_]ppv[-_](\d+)", unknown_text, re.I)
    if not m:
        return None

    video_id = m.group(1)
    video_id = f"FC2-PPV-{video_id}"
    return await _fetch(video_id)


class _JavbeeDetailedProduct(DetailedProduct):
    def __init__(self, *, video_id: str, url: str, title: str) -> None:
        super().__init__()

        self._vid = video_id
        self._url = url
        self._title = title

    @property
    @override
    def sauce(self) -> str:
        return "javbee"

    @property
    @override
    def id(self) -> str:
        return self._vid

    @property
    @override
    def url(self) -> str:
        return self._url

    @property
    @override
    def title(self) -> str:
        return self._title

    @property
    @override
    def actresses(self) -> list[str]:
        return []


async def _fetch(video_id: str) -> DetailedProduct | None:
    soup = await get_html(
        "https://javbee.me/search",
        queries={
            "keyword": video_id,
        },
    )
    if not soup:
        return None

    anchor = soup.select_one(".title > a")
    if not anchor:
        return None

    url = anchor.get("href")
    if not url:
        return None
    if not isinstance(url, str):
        return None

    title = anchor.get_text()
    title = normalize_name(title)
    return _JavbeeDetailedProduct(video_id=video_id, url=url, title=title)
