from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Product, Sale
from app.services.sales_service import SaleError, SalesService

sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/")
@login_required
def list_sales():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template("sales/list.html", sales=sales)


@sales_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_sale():
    products = Product.query.filter(Product.quantity > 0).order_by(Product.name).all()

    if request.method == "POST":
        requested_items = []
        for product in products:
            raw_quantity = request.form.get(f"qty_{product.id}", "0")
            try:
                quantity = int(raw_quantity or 0)
            except ValueError:
                flash(f"Invalid quantity for {product.name}.", "danger")
                return render_template("sales/new.html", products=products)
            if quantity > 0:
                requested_items.append({"product_id": product.id, "quantity": quantity})

        try:
            sale = SalesService.create_sale(
                user_id=current_user.id,
                payment_method=request.form.get("payment_method", "cash"),
                requested_items=requested_items,
            )
            flash("Sale completed successfully.", "success")
            return redirect(url_for("sales.receipt", sale_id=sale.id))
        except SaleError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

    return render_template("sales/new.html", products=products)


@sales_bp.route("/<int:sale_id>/receipt")
@login_required
def receipt(sale_id):
    sale = db.get_or_404(Sale, sale_id)
    return render_template("sales/receipt.html", sale=sale)
