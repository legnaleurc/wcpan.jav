from abc import ABCMeta, abstractmethod
from typing import Self, final, override


__all__ = ("Product", "DetailedProduct")


class Product(metaclass=ABCMeta):
    @property
    @abstractmethod
    def sauce(self) -> str: ...

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def url(self) -> str: ...

    @abstractmethod
    async def __call__(self) -> "DetailedProduct | None": ...


class DetailedProduct(Product):
    @final
    @override
    async def __call__(self) -> Self | None:
        return self

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def actresses(self) -> list[str]: ...
