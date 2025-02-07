from typing import override

from wcpan.jav.types import DetailedProduct, Product


class SimpleDetailedProduct(DetailedProduct):
    def __init__(self, *, product: Product, title: str, actresses: list[str]) -> None:
        super().__init__()

        self._product = product
        self._title = title
        self._actresses = actresses

    @property
    @override
    def sauce(self) -> str:
        return self._product.sauce

    @property
    @override
    def id(self) -> str:
        return self._product.id

    @property
    @override
    def url(self) -> str:
        return self._product.url

    @property
    @override
    def title(self) -> str:
        return self._title

    @property
    @override
    def actresses(self) -> list[str]:
        return self._actresses
