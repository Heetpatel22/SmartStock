"""
Receipt service implementing IReceiptGenerator.
Single Responsibility: Generates and formats unique receipt identifiers.
"""

from datetime import datetime, timezone
import uuid
from app.core.interfaces import IReceiptGenerator


class ReceiptGenerator(IReceiptGenerator):
    """Generates time-sequenced unique receipt numbers."""

    def __init__(self, prefix: str = "SS"):
        self.prefix = prefix

    def generate_receipt_number(self) -> str:
        now = datetime.now(timezone.utc)
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"{self.prefix}-{now:%Y%m%d%H%M%S}-{unique_suffix}"

