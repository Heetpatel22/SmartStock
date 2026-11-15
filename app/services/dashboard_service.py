"""
Dashboard Service module.
Demonstrates Single Responsibility (SRP): computes business metrics and KPI aggregations.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import func
from app import db
from app.models import Product, Sale


class DashboardService:
    """Service encapsulating KPI computations and dashboard data retrieval."""

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        today = datetime.now(timezone.utc).date()
        products_count = Product.query.count()
        total_units = db.session.query(func.coalesce(func.sum(Product.quantity), 0)).scalar() or 0
        low_stock_products = Product.query.filter(Product.quantity <= Product.reorder_level).all()
        total_revenue = db.session.query(func.coalesce(func.sum(Sale.total), 0)).scalar() or 0
        todays_sales = [sale for sale in Sale.query.all() if sale.created_at.date() == today]
        todays_revenue = sum(float(sale.total) for sale in todays_sales)
        recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()

        return {
            "products_count": products_count,
            "total_units": total_units,
            "low_stock_products": low_stock_products,
            "total_revenue": total_revenue,
            "todays_revenue": todays_revenue,
            "recent_sales": recent_sales,
        }

