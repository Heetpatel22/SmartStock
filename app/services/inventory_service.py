"""
Inventory Service module.

Demonstrates:
- Single Responsibility Principle (SRP): Only responsible for inventory adjustment business logic.
- Dependency Inversion Principle (DIP): Injected with IProductWriter and IStockMovementRecorder.
"""

from typing import Optional
from app import db
from app.core.exceptions import InventoryError
from app.core.interfaces import IProductWriter, IStockMovementRecorder
from app.models import Product, StockMovement
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_movement_repository import StockMovementRepository


class InventoryService:
    """Service encapsulating stock adjustment domain rules."""

    def __init__(
        self,
        product_writer: Optional[IProductWriter] = None,
        movement_recorder: Optional[IStockMovementRecorder] = None,
    ):
        self.product_writer = product_writer or ProductRepository()
        self.movement_recorder = movement_recorder or StockMovementRepository()

    def adjust(self, product: Product, quantity_change: int, reason: str = "") -> StockMovement:
        """
        Adjust stock quantity following domain constraints.
        Raises InventoryError if stock falls below zero.
        """
        if quantity_change == 0:
            raise InventoryError("Adjustment quantity cannot be zero.")

        new_quantity = product.quantity + quantity_change
        if new_quantity < 0:
            raise InventoryError("Stock cannot fall below zero.")

        product.quantity = new_quantity
        self.product_writer.save(product)

        movement_type = "IN" if quantity_change > 0 else "OUT"
        clean_reason = reason.strip() if reason and reason.strip() else "Manual adjustment"
        movement = self.movement_recorder.record_movement(
            product_id=product.id,
            movement_type=movement_type,
            quantity=abs(quantity_change),
            reason=clean_reason,
        )

        if hasattr(self.product_writer, "commit"):
            self.product_writer.commit()
        elif hasattr(self.movement_recorder, "commit"):
            self.movement_recorder.commit()

        return movement

    @staticmethod
    def adjust_stock(product: Product, quantity_change: int, reason: str = "") -> StockMovement:
        """Class/static convenience method maintaining backward compatibility."""
        service = InventoryService()
        return service.adjust(product, quantity_change, reason)
