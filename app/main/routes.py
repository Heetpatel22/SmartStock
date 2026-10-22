from datetime import datetime, timezone

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.models import Product, Sale

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    today = datetime.now(timezone.utc).date()
    products_count = Product.query.count()
    total_units = db.session.query(func.coalesce(func.sum(Product.quantity), 0)).scalar()
    low_stock_products = Product.query.filter(Product.quantity <= Product.reorder_level).all()
    total_revenue = db.session.query(func.coalesce(func.sum(Sale.total), 0)).scalar()
    todays_sales = [sale for sale in Sale.query.all() if sale.created_at.date() == today]
    todays_revenue = sum(float(sale.total) for sale in todays_sales)
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()

    return render_template(
        "main/dashboard.html",
        products_count=products_count,
        total_units=total_units,
        low_stock_products=low_stock_products,
        total_revenue=total_revenue,
        todays_revenue=todays_revenue,
        recent_sales=recent_sales,
    )
