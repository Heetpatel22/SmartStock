"""
Supplier repository implementing ISupplierRepository.
Encapsulates all SQLAlchemy data access for Supplier models.
"""

from typing import List, Optional
from app import db
from app.core.interfaces import ISupplierRepository
from app.models import Supplier


class SupplierRepository(ISupplierRepository):
    """Concrete repository for Supplier operations."""

    def __init__(self, session=None):
        self._session = session or db.session

    def get_all(self) -> List[Supplier]:
        return self._session.query(Supplier).order_by(Supplier.name).all()

    def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        return self._session.get(Supplier, supplier_id)

    def save(self, supplier: Supplier) -> Supplier:
        self._session.add(supplier)
        self._session.flush()
        return supplier

    def commit(self) -> None:
        self._session.commit()

