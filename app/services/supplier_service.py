"""
Supplier Service module.
Demonstrates Single Responsibility (SRP) and Dependency Inversion (DIP).
"""

from typing import List, Optional
from app.core.exceptions import ValidationError
from app.core.interfaces import ISupplierRepository
from app.models import Supplier
from app.repositories.supplier_repository import SupplierRepository


class SupplierService:
    """Domain service for supplier management."""

    def __init__(self, supplier_repo: Optional[ISupplierRepository] = None):
        self.supplier_repo = supplier_repo or SupplierRepository()

    def get_all(self) -> List[Supplier]:
        return self.supplier_repo.get_all()

    def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        return self.supplier_repo.get_by_id(supplier_id)

    def create_supplier(self, name: str, phone: str = "", email: str = "", address: str = "") -> Supplier:
        clean_name = name.strip()
        if not clean_name:
            raise ValidationError("Supplier name is required.")

        supplier = Supplier(
            name=clean_name,
            phone=phone.strip() if phone else "",
            email=email.strip() if email else "",
            address=address.strip() if address else "",
        )
        self.supplier_repo.save(supplier)
        if hasattr(self.supplier_repo, "commit"):
            self.supplier_repo.commit()
        return supplier

    def update_supplier(self, supplier_id: int, name: str, phone: str = "", email: str = "", address: str = "") -> Supplier:
        supplier = self.get_by_id(supplier_id)
        if not supplier:
            raise ValidationError("Supplier not found.")

        clean_name = name.strip()
        if not clean_name:
            raise ValidationError("Supplier name is required.")

        supplier.name = clean_name
        supplier.phone = phone.strip() if phone else ""
        supplier.email = email.strip() if email else ""
        supplier.address = address.strip() if address else ""

        self.supplier_repo.save(supplier)
        if hasattr(self.supplier_repo, "commit"):
            self.supplier_repo.commit()
        return supplier

