"""
Product repository implementing IProductReader and IProductWriter.
Encapsulates all SQLAlchemy data access for Product models.
"""

from typing import Any, List, Optional
from app import db
from app.core.interfaces import IProductReader, IProductWriter
from app.models import Product


class ProductRepository(IProductReader, IProductWriter):
    """Concrete repository for Product persistence using Flask-SQLAlchemy."""

    def __init__(self, session=None):
        self._session = session or db.session

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self._session.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self._session.query(Product).filter_by(sku=sku).first()

    def get_all_in_stock(self) -> List[Product]:
        return (
            self._session.query(Product)
            .filter(Product.quantity > 0)
            .order_by(Product.name)
            .all()
        )

    def get_all(self) -> List[Product]:
        return self._session.query(Product).order_by(Product.name).all()

    def update_quantity(self, product_id: int, new_quantity: int) -> Product:
        product = self.get_by_id(product_id)
        if product:
            product.quantity = new_quantity
            self._session.flush()
        return product

    def save(self, product: Product) -> Product:
        self._session.add(product)
        self._session.flush()
        return product
