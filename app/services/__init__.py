"""
Services package for SmartStock.
Contains domain business logic adhering to SOLID principles.
"""

from app.services.inventory_service import InventoryError, InventoryService
from app.services.sales_service import SaleError, SalesService
from app.services.receipt_service import ReceiptGenerator
from app.services.payment_strategies import (
    BasePaymentStrategy,
    CashPaymentStrategy,
    CardPaymentStrategy,
    MobilePaymentStrategy,
    UPIPaymentStrategy,
    PaymentProcessorRegistry,
)

__all__ = [
    "InventoryError",
    "InventoryService",
    "SaleError",
    "SalesService",
    "ReceiptGenerator",
    "BasePaymentStrategy",
    "CashPaymentStrategy",
    "CardPaymentStrategy",
    "MobilePaymentStrategy",
    "UPIPaymentStrategy",
    "PaymentProcessorRegistry",
]

