"""
Repository package for SmartStock.
Separates data access from domain logic (Single Responsibility & Dependency Inversion).
"""

from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.stock_movement_repository import StockMovementRepository

__all__ = [
    "ProductRepository",
    "SaleRepository",
    "StockMovementRepository",
]
