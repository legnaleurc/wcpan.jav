import asyncio
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import NoReturn

from ._sauces.lib import generate_detailed_products, generate_products


@dataclass(frozen=True, kw_only=True)
class Arguments:
    id: str
    detailed: bool


async def _amain(args: list[str]) -> int:
    kwargs = _parse_args(args)

    if kwargs.detailed:
        await _show_detailed_products(kwargs.id)
    else:
        await _show_products(kwargs.id)

    return 0


def _parse_args(args: list[str]) -> Arguments:
    parser = ArgumentParser("wcpan.jav")
    parser.add_argument("--detailed", "-d", action="store_true", default=False)
    parser.add_argument("id", type=str)

    kwargs = parser.parse_args(args)
    return Arguments(
        id=kwargs.id,
        detailed=kwargs.detailed,
    )


async def _show_products(id: str) -> None:
    async for product in generate_products(id):
        print(f"- sauce: {product.sauce}")
        print(f"  id: {product.id}")
        print(f"  url: {product.url}")


async def _show_detailed_products(id: str) -> None:
    async for product in generate_detailed_products(id):
        print(f"- sauce: {product.sauce}")
        print(f"  id: {product.id}")
        print(f"  url: {product.url}")
        print(f"  title: {product.title}")
        print(f"  actresses: {product.actresses}")


def run_as_module() -> NoReturn:
    sys.exit(asyncio.run(_amain(sys.argv[1:])))
