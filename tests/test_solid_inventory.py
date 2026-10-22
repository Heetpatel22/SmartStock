"""
TDD Unit Tests for InventoryService (Module 1).

Applies Test-Driven Development (TDD) using xUnit (pytest).
Demonstrates:
- Single Responsibility Principle (SRP): Tests stock adjustments independently.
- Dependency Inversion Principle (DIP): Injects fake/in-memory IProductWriter
  and IStockMovementRecorder test doubles without touching a live database.
"""

from decimal import Decimal
import pytest
from app.core.exceptions import InventoryError
from app.services.inventory_service import InventoryService


class FakeProduct:
    """In-memory test double representing a product."""

    def __init__(self, id: int, name: str, sku: str, quantity: int):
        self.id = id
        self.name = name
        self.sku = sku
        self.quantity = quantity
        self.cost_price = Decimal("10.00")
        self.selling_price = Decimal("20.00")


class FakeProductWriter:
    """In-memory test double conforming to IProductWriter (ISP/DIP)."""

    def __init__(self):
        self.saved_products = []

    def update_quantity(self, product_id: int, new_quantity: int):
        for prod in self.saved_products:
            if prod.id == product_id:
                prod.quantity = new_quantity
                return prod
        return None

    def save(self, product):
        self.saved_products.append(product)
        return product


class FakeMovementRecorder:
    """In-memory test double conforming to IStockMovementRecorder (ISP/DIP)."""

    def __init__(self):
        self.movements = []

    def record_movement(self, product_id: int, movement_type: str, quantity: int, reason: str):
        record = {
            "product_id": product_id,
            "movement_type": movement_type,
            "quantity": quantity,
            "reason": reason,
        }
        self.movements.append(record)
        return record


class TestInventoryServiceTDD:
    """Test suite for InventoryService domain logic."""

    def test_stock_increase_records_movement_in(self):
        # Arrange
        writer = FakeProductWriter()
        recorder = FakeMovementRecorder()
        service = InventoryService(product_writer=writer, movement_recorder=recorder)
        product = FakeProduct(id=1, name="Keyboard", sku="KB-001", quantity=10)

        # Act
        service.adjust(product, quantity_change=5, reason="Restock")

        # Assert
        assert product.quantity == 15
        assert len(recorder.movements) == 1
        assert recorder.movements[0]["movement_type"] == "IN"
        assert recorder.movements[0]["quantity"] == 5
        assert recorder.movements[0]["reason"] == "Restock"

    def test_stock_decrease_records_movement_out(self):
        # Arrange
        writer = FakeProductWriter()
        recorder = FakeMovementRecorder()
        service = InventoryService(product_writer=writer, movement_recorder=recorder)
        product = FakeProduct(id=1, name="Mouse", sku="MS-001", quantity=10)

        # Act
        service.adjust(product, quantity_change=-4, reason="Damaged items")

        # Assert
        assert product.quantity == 6
        assert len(recorder.movements) == 1
        assert recorder.movements[0]["movement_type"] == "OUT"
        assert recorder.movements[0]["quantity"] == 4
        assert recorder.movements[0]["reason"] == "Damaged items"

    def test_stock_cannot_fall_below_zero(self):
        # Arrange
        writer = FakeProductWriter()
        recorder = FakeMovementRecorder()
        service = InventoryService(product_writer=writer, movement_recorder=recorder)
        product = FakeProduct(id=1, name="Monitor", sku="MN-001", quantity=5)

        # Act & Assert
        with pytest.raises(InventoryError, match="Stock cannot fall below zero"):
            service.adjust(product, quantity_change=-6, reason="Defective")

        # Invariant check: quantity remains untouched and no movement is recorded
        assert product.quantity == 5
        assert len(recorder.movements) == 0

    def test_zero_quantity_adjustment_rejected(self):
        # Arrange
        writer = FakeProductWriter()
        recorder = FakeMovementRecorder()
        service = InventoryService(product_writer=writer, movement_recorder=recorder)
        product = FakeProduct(id=1, name="Desk Mat", sku="DM-001", quantity=10)

        # Act & Assert
        with pytest.raises(InventoryError, match="Adjustment quantity cannot be zero"):
            service.adjust(product, quantity_change=0, reason="No-op")
