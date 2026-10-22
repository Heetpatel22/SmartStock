"""
Core interfaces and protocols for SmartStock.

Demonstrates:
- Interface Segregation Principle (ISP): Clients only depend on small, focused interfaces
  they actually need (e.g., IProductReader vs IProductWriter).
- Dependency Inversion Principle (DIP): High-level business logic modules depend on these
  abstractions rather than concrete database/ORM implementations.
"""

from decimal import Decimal
from typing import Any, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IProductReader(Protocol):
    """Interface for reading product and catalog data (ISP)."""

    def get_by_id(self, product_id: int) -> Optional[Any]:
        """Retrieve a product by its ID."""
        ...

    def get_by_sku(self, sku: str) -> Optional[Any]:
        """Retrieve a product by its SKU."""
        ...

    def get_all_in_stock(self) -> List[Any]:
        """Retrieve all products with quantity > 0."""
        ...


@runtime_checkable
class IProductWriter(Protocol):
    """Interface for modifying product inventory and details (ISP)."""

    def update_quantity(self, product_id: int, new_quantity: int) -> Any:
        """Update product quantity in the store."""
        ...

    def save(self, product: Any) -> Any:
        """Persist product changes."""
        ...


@runtime_checkable
class IStockMovementRecorder(Protocol):
    """Interface for logging stock movements (Single Responsibility)."""

    def record_movement(
        self, product_id: int, movement_type: str, quantity: int, reason: str
    ) -> Any:
        """Log a stock movement record (IN / OUT)."""
        ...


@runtime_checkable
class ISaleRecorder(Protocol):
    """Interface for persisting sales transactions and line items (ISP)."""

    def record_sale(
        self,
        receipt_number: str,
        total: Decimal,
        payment_method: str,
        user_id: int,
        items_data: List[dict],
    ) -> Any:
        """Persist a completed sale and its line items."""
        ...

    def get_sale_by_id(self, sale_id: int) -> Optional[Any]:
        """Fetch sale by ID."""
        ...

    def get_all_sales(self) -> List[Any]:
        """Fetch all sales records."""
        ...


@runtime_checkable
class IReceiptGenerator(Protocol):
    """Interface for receipt identifier generation (Single Responsibility)."""

    def generate_receipt_number(self) -> str:
        """Generate a unique human-readable receipt identifier."""
        ...


@runtime_checkable
class IPaymentStrategy(Protocol):
    """
    Strategy interface for payment methods.
    Demonstrates Open/Closed Principle (OCP) and Liskov Substitution Principle (LSP).
    """

    def supports(self, payment_method: str) -> bool:
        """Check if this strategy handles the given payment method name."""
        ...

    def process(self, amount: Decimal, **kwargs) -> bool:
        """Validate and process payment for the given amount."""
        ...
