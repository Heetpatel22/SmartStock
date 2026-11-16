"""
Product Service module.

Demonstrates:
- Single Responsibility Principle (SRP): Coordinates product domain logic, validation,
  and audit logging.
- Dependency Inversion Principle (DIP): Injected with repository interfaces rather than
  tight coupling to Flask or SQLAlchemy sessions.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from app.core.exceptions import ValidationError
from app.core.interfaces import (
    ICategoryRepository,
    IProductDeleter,
    IProductReader,
    IProductWriter,
    IStockMovementRecorder,
    ISupplierRepository,
)
from app.models import Category, Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_movement_repository import StockMovementRepository
from app.repositories.supplier_repository import SupplierRepository


class ProductService:
    """High-level domain service for managing the product catalog and categories."""

    def __init__(
        self,
        product_repo: Optional[Any] = None,
        movement_recorder: Optional[IStockMovementRecorder] = None,
        category_repo: Optional[ICategoryRepository] = None,
        supplier_repo: Optional[ISupplierRepository] = None,
    ):
        prod = product_repo or ProductRepository()
        self.product_reader: IProductReader = prod
        self.product_writer: IProductWriter = prod
        self.product_deleter: IProductDeleter = prod
        self.product_repo = prod
        self.movement_recorder = movement_recorder or StockMovementRepository()
        self.category_repo = category_repo or CategoryRepository()
        self.supplier_repo = supplier_repo or SupplierRepository()

    def get_catalog(self, search: Optional[str] = None) -> List[Product]:
        return self.product_reader.get_all(search=search)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.product_reader.get_by_id(product_id)

    def create_product(
        self,
        sku: str,
        name: str,
        description: str = "",
        cost_price: Any = "0.00",
        selling_price: Any = "0.00",
        quantity: int = 0,
        reorder_level: int = 5,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
    ) -> Product:
        clean_sku = sku.strip().upper()
        clean_name = name.strip()

        if not clean_sku or not clean_name:
            raise ValidationError("SKU and product name are required.")

        if self.product_reader.get_by_sku(clean_sku):
            raise ValidationError(f"SKU '{clean_sku}' is already in use.")

        try:
            cp = Decimal(str(cost_price))
            sp = Decimal(str(selling_price))
            qty = int(quantity)
            reorder = int(reorder_level)
            if cp < 0 or sp <= 0:
                raise ValidationError("Prices must be valid positive amounts.")
            if qty < 0 or reorder < 0:
                raise ValidationError("Stock quantities cannot be negative.")
        except (ValueError, InvalidOperation):
            raise ValidationError("Invalid numeric values for price or quantity.")

        product = Product(
            sku=clean_sku,
            name=clean_name,
            description=description.strip() if description else "",
            cost_price=cp,
            selling_price=sp,
            quantity=qty,
            reorder_level=reorder,
            category_id=category_id if category_id else None,
            supplier_id=supplier_id if supplier_id else None,
        )
        self.product_writer.save(product)

        if qty > 0:
            self.movement_recorder.record_movement(
                product_id=product.id,
                movement_type="IN",
                quantity=qty,
                reason="Opening stock",
            )

        if hasattr(self.product_repo, "commit"):
            self.product_repo.commit()

        return product

    @staticmethod
    def _update_integer(value: Any, label: str) -> int:
        # JSON booleans and fractional numbers must not be silently coerced.
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValidationError(f"{label} must be a whole number.") from None
        if (not number.is_finite() or number != number.to_integral_value()
                or number < 0 or number > 2**63 - 1):
            raise ValidationError(f"{label} must be a non-negative whole number.")
        return int(number)

    def update_product(self, product_id: int, updates: Dict[str, Any]) -> Product:
        product = self.get_by_id(product_id)
        if not product:
            raise ValidationError("Product not found.")
        if not isinstance(updates, dict):
            raise ValidationError("Product updates must be an object.")

        # Validate the entire request before touching the tracked ORM object.
        # A later validation query can otherwise autoflush an earlier edit.
        changes = {}
        for field, label in (("sku", "SKU"), ("name", "Product name")):
            if field in updates:
                value = updates[field]
                if not isinstance(value, str) or not value.strip():
                    raise ValidationError(f"{label} must be a non-empty string.")
                changes[field] = value.strip().upper() if field == "sku" else value.strip()
        if "sku" in changes:
            existing = self.product_reader.get_by_sku(changes["sku"])
            if existing and existing.id != product.id:
                raise ValidationError(f"SKU '{changes['sku']}' is already in use.")

        if "description" in updates:
            value = updates["description"]
            if value is not None and not isinstance(value, str):
                raise ValidationError("Description must be a string.")
            changes["description"] = (value or "").strip()

        for field, label in (("cost_price", "Cost price"), ("selling_price", "Selling price")):
            if field in updates:
                try:
                    value = Decimal(str(updates[field]))
                except (InvalidOperation, ValueError):
                    raise ValidationError(f"{label} must be a finite amount.") from None
                if not value.is_finite() or value < 0 or (field == "selling_price" and value == 0):
                    raise ValidationError(f"{label} must be a valid positive amount.")
                changes[field] = value

        for field, label in (("quantity", "Quantity"), ("reorder_level", "Reorder level")):
            if field in updates:
                changes[field] = self._update_integer(updates[field], label)

        for field, label, repo in (("category_id", "Category", self.category_repo),
                                   ("supplier_id", "Supplier", self.supplier_repo)):
            if field in updates:
                value = updates[field]
                if value is None or value == "":
                    changes[field] = None
                else:
                    related_id = self._update_integer(value, label + " ID")
                    if not repo.get_by_id(related_id):
                        raise ValidationError(f"{label} not found.")
                    changes[field] = related_id

        original_quantity = product.quantity
        try:
            for field, value in changes.items():
                setattr(product, field, value)
            diff = product.quantity - original_quantity
            if diff:
                self.movement_recorder.record_movement(
                    product_id=product.id,
                    movement_type="IN" if diff > 0 else "OUT",
                    quantity=abs(diff),
                    reason="Product edit",
                )
            self.product_writer.save(product)
            if hasattr(self.product_repo, "commit"):
                self.product_repo.commit()
        except Exception:
            if hasattr(self.product_repo, "rollback"):
                self.product_repo.rollback()
            raise
        return product

    def delete_product(self, product_id: int) -> None:
        product = self.get_by_id(product_id)
        if not product:
            raise ValidationError("Product not found.")

        # Safeguard: prevent deletion if sales records exist
        if product.sale_items:
            raise ValidationError("Products with recorded sales cannot be deleted.")

        self.product_deleter.delete(product)

        if hasattr(self.product_repo, "commit"):
            self.product_repo.commit()

    def create_category(self, name: str) -> Category:
        clean = name.strip()
        if not clean:
            raise ValidationError("Category name is required.")
        if self.category_repo.get_by_name(clean):
            raise ValidationError(f"Category '{clean}' already exists.")
        category = Category(name=clean)
        self.category_repo.save(category)
        if hasattr(self.category_repo, "commit"):
            self.category_repo.commit()
        return category

    def delete_category(self, category_id: int) -> None:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValidationError("Category not found.")
        if category.products:
            raise ValidationError("A category assigned to products cannot be deleted.")
        self.category_repo.delete(category)
        if hasattr(self.category_repo, "commit"):
            self.category_repo.commit()

