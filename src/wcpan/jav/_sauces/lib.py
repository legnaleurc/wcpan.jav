from asyncio import as_completed
from collections.abc import AsyncIterator, Awaitable, Callable
from logging import getLogger

from wcpan.jav.types import DetailedProduct, Product

from ._1pondo import fetch as _1pondo
from ._10musume import fetch as _10musume
from ._carib import fetch as _carib
from ._caribpr import fetch as _caribpr
from ._fanza import fetch as _fanza
from ._fc2 import fetch as _fc2
from ._heydouga import fetch as _heydouga
from ._heyzo import fetch as _heyzo
from ._javbee import fetch as _javbee
from ._mgstage import fetch as _mgstage
from ._tokyohot import fetch as _tokyohot


type Fetch = Callable[[str], Awaitable[Product | None]]


_L = getLogger(__name__)
_SAUCES: list[Fetch] = [
    _10musume,
    _1pondo,
    _carib,
    _caribpr,
    _fanza,
    _fc2,
    _heydouga,
    _heyzo,
    _javbee,
    _mgstage,
    _tokyohot,
]


def generate_products(unknwon_text: str) -> AsyncIterator[Product]:
    tasks = (_(unknwon_text) for _ in _SAUCES)
    no_raise_tasks = (_no_raise(_) for _ in tasks)
    maybe_products = (await _ for _ in as_completed(no_raise_tasks))
    products = (_ async for _ in maybe_products if _)
    return products


def generate_detailed_products(unknown_text: str) -> AsyncIterator[DetailedProduct]:
    tasks = (_() async for _ in generate_products(unknown_text))
    no_raise_tasks = (await _no_raise(_) async for _ in tasks)
    detailed_products = (_ async for _ in no_raise_tasks if _)
    return detailed_products


async def _no_raise[T](aw: Awaitable[T]) -> T | None:
    try:
        return await aw
    except Exception:
        _L.exception("sauce error")
        return None
