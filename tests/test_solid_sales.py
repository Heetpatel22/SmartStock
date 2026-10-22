"""
TDD Unit Tests for SalesService (Module 2).

Applies Test-Driven Development (TDD) using xUnit (pytest).
Demonstrates:
- Single Responsibility Principle (SRP): Isolates checkout calculation, validation,
  and transaction assembly.
- Open/Closed Principle (OCP): Verifies checkout with pluggable payment strategies.
- Dependency Inversion Principle (DIP): Injects purely in-memory repository doubles.
"""

from decimal import Decimal
import pytest
from app.core.exceptions import PaymentError, SaleError
from app.services.sales_service import SalesService
from app.services.payment_strategies import PaymentProcessorRegistry


class FakeProduct:
    def __init__(self, id: int, name: str, sku: str, quantity: int, price: str):
        self.id = id
        self.name = name
        self.sku = sku
        self.quantity = quantity
        self.selling_price = Decimal(price)


class FakeProductRepo:
    """Implements IProductReader and IProductWriter in memory."""

    def __init__(self, products=None):
        self._products = {p.id: p for p in (products or [])}

    def get_by_id(self, product_id: int):
        return self._products.get(product_id)

    def get_by_sku(self, sku: str):
        for p in self._products.values():
            if p.sku == sku:
                return p
        return None

    def get_all_in_stock(self):
        return [p for p in self._products.values() if p.quantity > 0]

    def update_quantity(self, product_id: int, new_quantity: int):
        prod = self._products.get(product_id)
        if prod:
            prod.quantity = new_quantity
        return prod

    def save(self, product):
        self._products[product.id] = product
        return product


class FakeSaleRecorder:
    """Implements ISaleRecorder in memory."""

    def __init__(self):
        self.recorded_sales = []

    def record_sale(self, receipt_number, total, payment_method, user_id, items_data):
        record = {
            "receipt_number": receipt_number,
            "total": total,
            "payment_method": payment_method,
            "user_id": user_id,
            "items": items_data,
        }
        self.recorded_sales.append(record)
        return record

    def get_sale_by_id(self, sale_id):
        return None

    def get_all_sales(self):
        return self.recorded_sales

    def commit(self):
        pass


class FakeMovementRecorder:
    """Implements IStockMovementRecorder in memory."""

    def __init__(self):
        self.movements = []

    def record_movement(self, product_id, movement_type, quantity, reason):
        movement = {
            "product_id": product_id,
            "movement_type": movement_type,
            "quantity": quantity,
            "reason": reason,
        }
        self.movements.append(movement)
        return movement


class FakeReceiptGenerator:
    """Implements IReceiptGenerator."""

    def __init__(self, receipt_to_return="TEST-REC-001"):
        self.receipt_to_return = receipt_to_return

    def generate_receipt_number(self):
        return self.receipt_to_return


class TestSalesServiceTDD:
    """TDD test cases for SalesService checkout domain logic."""

    def test_successful_checkout_calculates_total_and_deducts_stock(self):
        # Arrange
        p1 = FakeProduct(id=1, name="Item 1", sku="ITM-1", quantity=10, price="15.00")
        p2 = FakeProduct(id=2, name="Item 2", sku="ITM-2", quantity=5, price="25.50")
        prod_repo = FakeProductRepo([p1, p2])
        sale_recorder = FakeSaleRecorder()
        movement_recorder = FakeMovementRecorder()
        receipt_gen = FakeReceiptGenerator("REC-999")

        service = SalesService(
            product_reader=prod_repo,
            product_writer=prod_repo,
            sale_recorder=sale_recorder,
            movement_recorder=movement_recorder,
            receipt_generator=receipt_gen,
            payment_registry=PaymentProcessorRegistry(),
        )

        requested = [
            {"product_id": 1, "quantity": 2},  # 2 * 15.00 = 30.00
            {"product_id": 2, "quantity": 1},  # 1 * 25.50 = 25.50
        ]

        # Act
        result = service.checkout(user_id=42, payment_method="cash", requested_items=requested)

        # Assert
        assert result["total"] == Decimal("55.50")
        assert result["receipt_number"] == "REC-999"
        assert p1.quantity == 8
        assert p2.quantity == 4
        assert len(movement_recorder.movements) == 2
        assert movement_recorder.movements[0]["movement_type"] == "OUT"
        assert movement_recorder.movements[0]["quantity"] == 2

    def test_checkout_fails_when_requested_quantity_exceeds_stock(self):
        # Arrange
        p1 = FakeProduct(id=1, name="Keyboard", sku="KB-1", quantity=3, price="50.00")
        prod_repo = FakeProductRepo([p1])
        service = SalesService(
            product_reader=prod_repo,
            product_writer=prod_repo,
            sale_recorder=FakeSaleRecorder(),
            movement_recorder=FakeMovementRecorder(),
        )

        # Act & Assert
        with pytest.raises(SaleError, match="Insufficient stock"):
            service.checkout(
                user_id=1,
                payment_method="cash",
                requested_items=[{"product_id": 1, "quantity": 5}],
            )

        # Invariant check: quantity remains untouched
        assert p1.quantity == 3

    def test_checkout_fails_on_unsupported_payment_method(self):
        # Arrange
        p1 = FakeProduct(id=1, name="Item", sku="ITM", quantity=10, price="10.00")
        prod_repo = FakeProductRepo([p1])
        service = SalesService(
            product_reader=prod_repo,
            product_writer=prod_repo,
            sale_recorder=FakeSaleRecorder(),
            movement_recorder=FakeMovementRecorder(),
        )

        # Act & Assert
        with pytest.raises(PaymentError, match="Unsupported payment method"):
            service.checkout(
                user_id=1,
                payment_method="unsupported_bitcoin",
                requested_items=[{"product_id": 1, "quantity": 1}],
            )

    def test_checkout_supports_indian_upi_payment(self):
        # Arrange (Verifies UPI payment strategy)
        p1 = FakeProduct(id=1, name="Cable", sku="CBL", quantity=10, price="250.00")
        prod_repo = FakeProductRepo([p1])
        sale_recorder = FakeSaleRecorder()
        service = SalesService(
            product_reader=prod_repo,
            product_writer=prod_repo,
            sale_recorder=sale_recorder,
            movement_recorder=FakeMovementRecorder(),
        )

        # Act
        result = service.checkout(
            user_id=1,
            payment_method="upi",
            requested_items=[{"product_id": 1, "quantity": 2}],
        )

        # Assert
        assert result["payment_method"] == "upi"
        assert result["total"] == Decimal("500.00")
