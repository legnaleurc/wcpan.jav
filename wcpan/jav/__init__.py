from importlib.metadata import version

from ._sauces.lib import generate_detailed_products as generate_detailed_products
from ._sauces.lib import generate_products as generate_products


__version__ = version(__package__ or __name__)
__all__ = ("generate_products", "generate_detailed_products")
