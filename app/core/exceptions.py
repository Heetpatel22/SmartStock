"""
Core domain exceptions for SmartStock.
Adheres to Liskov Substitution Principle (LSP) through a clean exception hierarchy.
"""


class SmartStockError(Exception):
    """Base exception for all domain errors in SmartStock."""
    pass


class InventoryError(SmartStockError, ValueError):
    """Raised when an inventory operation violates domain rules (e.g., negative stock)."""
    pass


class SaleError(SmartStockError, ValueError):
    """Raised when a sale operation violates domain rules (e.g., insufficient stock)."""
    pass


class PaymentError(SmartStockError, ValueError):
    """Raised when payment processing or validation fails."""
    pass


class ValidationError(SmartStockError, ValueError):
    """Raised when input validation fails."""
    pass

