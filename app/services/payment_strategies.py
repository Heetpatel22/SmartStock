"""
Payment strategy implementations.

Demonstrates:
- Open/Closed Principle (OCP): New payment methods (e.g., UPI, Gift Card, Crypto)
  can be added by extending BasePaymentStrategy without modifying existing code.
- Liskov Substitution Principle (LSP): All payment strategies conform to BasePaymentStrategy
  and can be substituted interchangeably without altering correctness.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional
from app.core.exceptions import PaymentError


class BasePaymentStrategy(ABC):
    """Abstract payment processor strategy (LSP & OCP)."""

    @abstractmethod
    def supports(self, payment_method: str) -> bool:
        """Check if payment method is supported by this strategy."""
        pass

    @abstractmethod
    def process(self, amount: Decimal, **kwargs) -> bool:
        """Process or validate the payment amount."""
        pass


class CashPaymentStrategy(BasePaymentStrategy):
    """Handles cash transactions."""

    def supports(self, payment_method: str) -> bool:
        return payment_method.strip().lower() == "cash"

    def process(self, amount: Decimal, **kwargs) -> bool:
        if amount < Decimal("0.00"):
            raise PaymentError("Cash payment amount cannot be negative.")
        return True


class CardPaymentStrategy(BasePaymentStrategy):
    """Handles credit/debit card transactions."""

    def supports(self, payment_method: str) -> bool:
        return payment_method.strip().lower() in ("card", "credit_card", "debit_card")

    def process(self, amount: Decimal, **kwargs) -> bool:
        if amount <= Decimal("0.00"):
            raise PaymentError("Card payment amount must be greater than zero.")
        return True


class MobilePaymentStrategy(BasePaymentStrategy):
    """Handles mobile wallet transactions."""

    def supports(self, payment_method: str) -> bool:
        return payment_method.strip().lower() in ("mobile", "mobile_payment", "wallet")

    def process(self, amount: Decimal, **kwargs) -> bool:
        if amount <= Decimal("0.00"):
            raise PaymentError("Mobile payment amount must be greater than zero.")
        return True


class UPIPaymentStrategy(BasePaymentStrategy):
    """Handles Indian Unified Payments Interface (UPI) transactions."""

    def supports(self, payment_method: str) -> bool:
        return payment_method.strip().lower() in ("upi", "gpay", "phonepe", "paytm")

    def process(self, amount: Decimal, **kwargs) -> bool:
        if amount <= Decimal("0.00"):
            raise PaymentError("UPI transaction amount must be greater than zero.")
        return True


class PaymentProcessorRegistry:
    """
    Registry for payment strategies.
    Adheres to Open/Closed Principle: Register new strategies at runtime.
    """

    def __init__(self):
        self._strategies: list[BasePaymentStrategy] = []
        self._register_default_strategies()

    def _register_default_strategies(self):
        self.register(CashPaymentStrategy())
        self.register(CardPaymentStrategy())
        self.register(MobilePaymentStrategy())
        self.register(UPIPaymentStrategy())

    def register(self, strategy: BasePaymentStrategy) -> None:
        """Register a new payment strategy (Open for extension)."""
        self._strategies.append(strategy)

    def get_strategy(self, payment_method: str) -> Optional[BasePaymentStrategy]:
        """Find a strategy supporting the specified method."""
        for strategy in self._strategies:
            if strategy.supports(payment_method):
                return strategy
        return None

    def process(self, payment_method: str, amount: Decimal, **kwargs) -> bool:
        """Locate strategy and execute payment."""
        strategy = self.get_strategy(payment_method)
        if not strategy:
            raise PaymentError(f"Unsupported payment method: '{payment_method}'.")
        return strategy.process(amount, **kwargs)
