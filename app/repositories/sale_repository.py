"""
Sale repository implementing ISaleRecorder.
Encapsulates transaction-safe persistence for sales and items.
"""

from decimal import Decimal
from typing import Any, List, Optional
from app import db
from app.core.interfaces import ISaleRecorder
from app.models import Sale, SaleItem


class SaleRepository(ISaleRecorder):
    """Concrete repository for Sale transactions."""

    def __init__(self, session=None):
        self._session = session or db.session

    def record_sale(
        self,
        receipt_number: str,
        total: Decimal,
        payment_method: str,
        user_id: int,
        items_data: List[dict],
    ) -> Sale:
        sale = Sale(
            receipt_number=receipt_number,
            total=total,
            payment_method=payment_method,
            user_id=user_id,
        )
        self._session.add(sale)
        self._session.flush()

        for item in items_data:
            sale_item = SaleItem(
                sale=sale,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )
            self._session.add(sale_item)

        self._session.flush()
        return sale

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        return self._session.get(Sale, sale_id)

    def get_all_sales(self) -> List[Sale]:
        return self._session.query(Sale).order_by(Sale.created_at.desc()).all()

    def commit(self) -> None:
        """Commit current transaction."""
        self._session.commit()
