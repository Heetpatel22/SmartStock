"""
Unit tests for Payment Strategies (OCP and LSP).

Demonstrates:
- Open/Closed Principle (OCP): Dynamic strategy registration and resolution.
- Liskov Substitution Principle (LSP): Uniform behavior across all BasePaymentStrategy implementations.
"""

from decimal import Decimal
import pytest
from app.core.exceptions import PaymentError
from app.services.payment_strategies import (
    BasePaymentStrategy,
    CardPaymentStrategy,
    CashPaymentStrategy,
    MobilePaymentStrategy,
    PaymentProcessorRegistry,
    UPIPaymentStrategy,
)


class CustomGiftCardStrategy(BasePaymentStrategy):
    """Custom payment strategy demonstrating OCP extension without modifying existing code."""

    def supports(self, payment_method: str) -> bool:
        return payment_method.strip().lower() == "gift_card"

    def process(self, amount: Decimal, **kwargs) -> bool:
        if amount > Decimal("5000.00"):
            raise PaymentError("Gift card limit exceeded.")
        return True


class TestPaymentStrategies:
    """Test suite for payment strategies and registry."""

    def test_cash_strategy_validation(self):
        cash = CashPaymentStrategy()
        assert cash.supports("cash")
        assert cash.supports("CASH")
        assert not cash.supports("card")
        assert cash.process(Decimal("100.00")) is True
        with pytest.raises(PaymentError, match="cannot be negative"):
            cash.process(Decimal("-10.00"))

    def test_card_strategy_validation(self):
        card = CardPaymentStrategy()
        assert card.supports("card")
        assert card.supports("credit_card")
        assert card.supports("debit_card")
        assert card.process(Decimal("50.00")) is True
        with pytest.raises(PaymentError, match="must be greater than zero"):
            card.process(Decimal("0.00"))

    def test_mobile_strategy_validation(self):
        mobile = MobilePaymentStrategy()
        assert mobile.supports("mobile")
        assert mobile.supports("wallet")
        assert mobile.process(Decimal("75.00")) is True

    def test_upi_strategy_validation(self):
        upi = UPIPaymentStrategy()
        assert upi.supports("upi")
        assert upi.supports("gpay")
        assert upi.supports("phonepe")
        assert upi.process(Decimal("999.00")) is True

    def test_open_closed_principle_dynamic_extension(self):
        """Demonstrates adding a new payment strategy without modifying existing classes."""
        registry = PaymentProcessorRegistry()

        # Before registration
        with pytest.raises(PaymentError, match="Unsupported payment method"):
            registry.process("gift_card", Decimal("200.00"))

        # Extend at runtime (OCP)
        registry.register(CustomGiftCardStrategy())

        # After registration - seamlessly handled
        assert registry.process("gift_card", Decimal("200.00")) is True

