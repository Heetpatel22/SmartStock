"""
Sales Service module.

Demonstrates:
- Single Responsibility Principle (SRP): Orchestrates sale checkout lifecycle.
- Open/Closed Principle (OCP): Integrates with PaymentProcessorRegistry for pluggable payments.
- Liskov Substitution Principle (LSP): Works transparently with any IPaymentStrategy or repository implementation.
- Interface Segregation Principle (ISP): Injects targeted interfaces (IProductReader, IProductWriter, ISaleRecorder, etc.).
- Dependency Inversion Principle (DIP): Injected dependencies with sensible defaults.
"""

from decimal import Decimal
from typing import List, Optional

from app.core.exceptions import SaleError
from app.core.interfaces import (
    IProductReader,
    IProductWriter,
    IReceiptGenerator,
    ISaleRecorder,
    IStockMovementRecorder,
)
from app.models import Sale
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.services.payment_strategies import PaymentProcessorRegistry
from app.services.receipt_service import ReceiptGenerator


class SalesService:
    """High-level domain service orchestrating sales and checkout."""

    def __init__(
        self,
        product_reader: Optional[IProductReader] = None,
        product_writer: Optional[IProductWriter] = None,
        sale_recorder: Optional[ISaleRecorder] = None,
        movement_recorder: Optional[IStockMovementRecorder] = None,
        receipt_generator: Optional[IReceiptGenerator] = None,
        payment_registry: Optional[PaymentProcessorRegistry] = None,
    ):
        prod_repo = ProductRepository()
        self.product_reader = product_reader or prod_repo
        self.product_writer = product_writer or prod_repo
        self.sale_recorder = sale_recorder or SaleRepository()
        self.movement_recorder = movement_recorder or StockMovementRepository()
        self.receipt_generator = receipt_generator or ReceiptGenerator()
        self.payment_registry = payment_registry or PaymentProcessorRegistry()

    def checkout(
        self, user_id: int, payment_method: str, requested_items: List[dict]
    ) -> Sale:
        """
        Executes complete checkout:
        1. Validates requested items and stock availability
        2. Calculates subtotals and grand total
        3. Validates and processes payment strategy
        4. Deducts inventory and logs stock movements
        5. Persists sale transaction and generates receipt
        """
        if not requested_items:
            raise SaleError("Select at least one product.")

        validated_items = []
        total = Decimal("0.00")

        # 1. Validation & pricing calculation (SRP)
        for requested in requested_items:
            product_id = int(requested.get("product_id", 0))
            quantity = int(requested.get("quantity", 0))

            product = self.product_reader.get_by_id(product_id)
            if not product:
                raise SaleError("A selected product no longer exists.")
            if quantity <= 0:
                raise SaleError("Sale quantities must be greater than zero.")
            if product.quantity < quantity:
                raise SaleError(
                    f"Insufficient stock for {product.name}. Available: {product.quantity}."
                )

            unit_price = Decimal(str(product.selling_price))
            subtotal = unit_price * quantity
            total += subtotal

            validated_items.append({
                "product": product,
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        # 2. Payment verification via Strategy Pattern (OCP / LSP)
        self.payment_registry.process(payment_method, total)

        # 3. Receipt generation (SRP)
        receipt_number = self.receipt_generator.generate_receipt_number()

        # 4. Inventory deduction & movement logging
        for item in validated_items:
            product = item["product"]
            new_quantity = product.quantity - item["quantity"]
            self.product_writer.update_quantity(product.id, new_quantity)
            self.movement_recorder.record_movement(
                product_id=product.id,
                movement_type="OUT",
                quantity=item["quantity"],
                reason=f"Sale {receipt_number}",
            )

        # 5. Persist sale and items via SaleRecorder (ISP / DIP)
        sale = self.sale_recorder.record_sale(
            receipt_number=receipt_number,
            total=total,
            payment_method=payment_method,
            user_id=user_id,
            items_data=validated_items,
        )

        if hasattr(self.sale_recorder, "commit"):
            self.sale_recorder.commit()
        return sale

    @staticmethod
    def create_sale(user_id: int, payment_method: str, requested_items: List[dict]) -> Sale:
        """Class/static convenience method maintaining backward compatibility."""
        service = SalesService()
        return service.checkout(user_id, payment_method, requested_items)
