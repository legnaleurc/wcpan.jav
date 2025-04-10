import re
from dataclasses import dataclass
from logging import getLogger
from pathlib import PurePath
from typing import override
from urllib.parse import quote, urlsplit, urlunsplit

from bs4 import Tag

from wcpan.jav.types import DetailedProduct, Product

from ._lib import get_html, normalize_name


_L = getLogger(__name__)


async def fetch(unknown_text: str) -> Product | None:
    m = re.search(r"(\w{2,6})[-_](\d{2,4}\w?)", unknown_text)
    if not m:
        return None

    video_id = _VideoId(m.group(1), m.group(2))
    return await _fetch(video_id)


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

    @property
    def query(self) -> str:
        return quote(f"{self.series}-{self.number}")

    def __str__(self) -> str:
        return f"{self.series}-{self.number}"

    def exclude(self, raw_id: str) -> str:
        return self._re.sub("", raw_id)


@dataclass(frozen=True, kw_only=True)
class _Variant:
    cid: str
    title: str
    url: str


class _FanzaDetailedProduct(DetailedProduct):
    def __init__(self, *, video_id: _VideoId, title: str, url: str) -> None:
        super().__init__()

        self._vid = video_id
        self._title = title
        self._url = url

    @property
    @override
    def sauce(self) -> str:
        return "fanza"

    @property
    @override
    def id(self) -> str:
        return str(self._vid)

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


async def _fetch(video_id: _VideoId) -> Product | None:
    soup = await get_html(
        "https://www.dmm.co.jp/age_check/=/declared=yes/",
        queries={
            "rurl": f"https://www.dmm.co.jp/search/=/searchstr={video_id.query}/",
        },
    )
    if not soup:
        return None

    anchor_list = soup.select(
        "div.border-r > div:nth-child(1) > div:nth-child(2) > a:nth-child(3)"
    )
    if not anchor_list:
        return None

    maybe_variants = (_get_variant(_, video_id) for _ in anchor_list)
    variants = filter(None, maybe_variants)
    ordered_list = sorted(variants, key=lambda _: _.cid)
    if not ordered_list:
        return None

    best = ordered_list[0]
    title = normalize_name(best.title)
    return _FanzaDetailedProduct(video_id=video_id, title=title, url=best.url)


def _get_variant(anchor: Tag, video_id: _VideoId) -> _Variant | None:
    title = anchor.get_text()
    if not title:
        return None

    raw_url = anchor.get("href")
    if not raw_url:
        return None
    if not isinstance(raw_url, str):
        return None

    try:
        parsed_url = urlsplit(raw_url)
    except Exception:
        _L.exception(f"invalid url {raw_url}")
        return None

    cid = _get_cid(parsed_url.path, video_id)
    url = urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            "",
            "",
        )
    )
    return _Variant(cid=cid, title=title, url=url)


# The original should have no prefix, should be the first after sorting.
def _get_cid(url_path: str, video_id: _VideoId) -> str:
    path = PurePath(url_path)
    last = path.parts[-1]
    raw_id = last.replace("cid=", "")
    return video_id.exclude(raw_id)
