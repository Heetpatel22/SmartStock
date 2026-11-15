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

    def update_product(self, product_id: int, updates: Dict[str, Any]) -> Product:
        product = self.get_by_id(product_id)
        if not product:
            raise ValidationError("Product not found.")

        original_quantity = product.quantity

        if "sku" in updates:
            new_sku = updates["sku"].strip().upper()
            if not new_sku:
                raise ValidationError("SKU cannot be empty.")
            existing = self.product_reader.get_by_sku(new_sku)
            if existing and existing.id != product.id:
                raise ValidationError(f"SKU '{new_sku}' is already in use.")
            product.sku = new_sku

        if "name" in updates:
            new_name = updates["name"].strip()
            if not new_name:
                raise ValidationError("Product name cannot be empty.")
            product.name = new_name

        if "description" in updates:
            product.description = (updates["description"] or "").strip()

        try:
            if "cost_price" in updates:
                cp = Decimal(str(updates["cost_price"]))
                if cp < 0:
                    raise ValidationError("Cost price cannot be negative.")
                product.cost_price = cp

            if "selling_price" in updates:
                sp = Decimal(str(updates["selling_price"]))
                if sp <= 0:
                    raise ValidationError("Selling price must be greater than zero.")
                product.selling_price = sp

            if "reorder_level" in updates:
                rl = int(updates["reorder_level"])
                if rl < 0:
                    raise ValidationError("Reorder level cannot be negative.")
                product.reorder_level = rl

            if "category_id" in updates:
                cid = updates["category_id"]
                product.category_id = int(cid) if cid else None

            if "supplier_id" in updates:
                sid = updates["supplier_id"]
                product.supplier_id = int(sid) if sid else None

            if "quantity" in updates:
                new_qty = int(updates["quantity"])
                if new_qty < 0:
                    raise ValidationError("Quantity cannot be negative.")
                diff = new_qty - original_quantity
                if diff != 0:
                    product.quantity = new_qty
                    self.movement_recorder.record_movement(
                        product_id=product.id,
                        movement_type="IN" if diff > 0 else "OUT",
                        quantity=abs(diff),
                        reason="Product edit",
                    )
        except (ValueError, InvalidOperation):
            raise ValidationError("Invalid numeric values supplied.")

        self.product_writer.save(product)

        if hasattr(self.product_repo, "commit"):
            self.product_repo.commit()

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

