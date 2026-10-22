from datetime import datetime, timezone
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


def _utc_now():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=_utc_now, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="cashier")

    sales = db.relationship("Sale", back_populates="cashier", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class Category(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship("Product", back_populates="category", lazy=True)


class Supplier(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))

    products = db.relationship("Product", back_populates="supplier", lazy=True)


class Product(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    selling_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=5)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"))

    category = db.relationship("Category", back_populates="products")
    supplier = db.relationship("Supplier", back_populates="products")
    sale_items = db.relationship("SaleItem", back_populates="product", lazy=True)
    stock_movements = db.relationship(
        "StockMovement",
        back_populates="product",
        lazy=True,
        cascade="all, delete-orphan",
    )

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def estimated_profit_per_unit(self):
        return Decimal(self.selling_price) - Decimal(self.cost_price)


class Sale(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    payment_method = db.Column(db.String(30), nullable=False, default="cash")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    cashier = db.relationship("User", back_populates="sales")
    items = db.relationship(
        "SaleItem",
        back_populates="sale",
        lazy=True,
        cascade="all, delete-orphan",
    )


class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sale.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    sale = db.relationship("Sale", back_populates="items")
    product = db.relationship("Product", back_populates="sale_items")


class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=_utc_now, nullable=False)

    product = db.relationship("Product", back_populates="stock_movements")
