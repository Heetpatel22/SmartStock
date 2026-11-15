"""
Repository package for SmartStock.
Separates data access from domain logic (Single Responsibility & Dependency Inversion).
"""

from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.repositories.supplier_repository import SupplierRepository

__all__ = [
    "CategoryRepository",
    "ProductRepository",
    "SaleRepository",
    "StockMovementRepository",
    "SupplierRepository",
]
