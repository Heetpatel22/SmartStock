"""
TDD Unit Tests for ProductService.

Demonstrates:
- Single Responsibility Principle (SRP): Isolates catalog manipulation and validation rules.
- Dependency Inversion Principle (DIP): Injects purely in-memory repository doubles.
"""

from decimal import Decimal
import pytest
from app.core.exceptions import ValidationError
from app.services.product_service import ProductService


class FakeProduct:
    def __init__(self, id: int, sku: str, name: str, cost_price: str, selling_price: str, quantity: int, reorder_level: int = 5):
        self.id = id
        self.sku = sku
        self.name = name
        self.cost_price = Decimal(cost_price)
        self.selling_price = Decimal(selling_price)
        self.quantity = quantity
        self.reorder_level = reorder_level
        self.description = ""
        self.category_id = None
        self.supplier_id = None
        self.sale_items = []


class FakeProductRepo:
    def __init__(self, products=None):
        self.products = {p.id: p for p in (products or [])}

    def get_by_id(self, product_id: int):
        return self.products.get(product_id)

    def get_by_sku(self, sku: str):
        for p in self.products.values():
            if p.sku == sku:
                return p
        return None

    def get_all(self, search=None):
        if search:
            return [p for p in self.products.values() if search.lower() in p.name.lower() or search.lower() in p.sku.lower()]
        return list(self.products.values())

    def save(self, product):
        if not hasattr(product, "id") or product.id is None:
            product.id = len(self.products) + 1
        self.products[product.id] = product
        return product

    def delete(self, product):
        if product.id in self.products:
            del self.products[product.id]

    def commit(self):
        pass


class FakeMovementRecorder:
    def __init__(self):
        self.movements = []

    def record_movement(self, product_id, movement_type, quantity, reason):
        rec = {"product_id": product_id, "movement_type": movement_type, "quantity": quantity, "reason": reason}
        self.movements.append(rec)
        return rec


class TestProductServiceSOLID:
    def test_create_product_success_and_logs_opening_stock(self):
        repo = FakeProductRepo()
        recorder = FakeMovementRecorder()
        service = ProductService(product_repo=repo, movement_recorder=recorder)

        prod = service.create_product(
            sku="MOUSE-01",
            name="Ergonomic Mouse",
            cost_price="500.00",
            selling_price="899.00",
            quantity=10,
        )

        assert prod.sku == "MOUSE-01"
        assert prod.quantity == 10
        assert len(recorder.movements) == 1
        assert recorder.movements[0]["movement_type"] == "IN"
        assert recorder.movements[0]["quantity"] == 10

    def test_create_product_rejects_duplicate_sku(self):
        existing = FakeProduct(1, "ELEC-100", "Existing Radio", "100.00", "150.00", 5)
        repo = FakeProductRepo([existing])
        service = ProductService(product_repo=repo)

        with pytest.raises(ValidationError, match="already in use"):
            service.create_product(
                sku="ELEC-100",
                name="Duplicate Radio",
                cost_price="100.00",
                selling_price="150.00",
                quantity=2,
            )

    def test_update_product_quantity_difference_logged(self):
        existing = FakeProduct(1, "ELEC-100", "Existing Radio", "100.00", "150.00", 10)
        repo = FakeProductRepo([existing])
        recorder = FakeMovementRecorder()
        service = ProductService(product_repo=repo, movement_recorder=recorder)

        updated = service.update_product(1, {"quantity": 16})
        assert updated.quantity == 16
        assert len(recorder.movements) == 1
        assert recorder.movements[0]["movement_type"] == "IN"
        assert recorder.movements[0]["quantity"] == 6

    def test_delete_product_safeguards_against_items_with_sales(self):
        existing = FakeProduct(1, "ELEC-100", "Existing Radio", "100.00", "150.00", 10)
        existing.sale_items = ["sale-1"]  # Has recorded sales
        repo = FakeProductRepo([existing])
        service = ProductService(product_repo=repo)

        with pytest.raises(ValidationError, match="Products with recorded sales cannot be deleted"):
            service.delete_product(1)

