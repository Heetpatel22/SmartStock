"""
Stock movement repository implementing IStockMovementRecorder.
Encapsulates logging of all stock audit movements (IN/OUT).
"""

from app import db
from app.core.interfaces import IStockMovementRecorder
from app.models import StockMovement


class StockMovementRepository(IStockMovementRecorder):
    """Concrete repository for audit tracking of stock adjustments."""

    def __init__(self, session=None):
        self._session = session or db.session

    def record_movement(
        self, product_id: int, movement_type: str, quantity: int, reason: str
    ) -> StockMovement:
        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason.strip() if reason else "Adjustment",
        )
        self._session.add(movement)
        self._session.flush()
        return movement

