"""
Sales routes (Presentation Layer).
Adheres to SRP and DIP by delegating to SalesService, SaleRepository, and ProductRepository.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.core.exceptions import SaleError
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.services.sales_service import SalesService

sales_bp = Blueprint("sales", __name__)
sale_repo = SaleRepository()
product_repo = ProductRepository()


@sales_bp.route("/")
@login_required
def list_sales():
    sales = sale_repo.get_all_sales()
    return render_template("sales/list.html", sales=sales)


@sales_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_sale():
    products = product_repo.get_all_in_stock()

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
            flash(str(exc), "danger")

    return render_template("sales/new.html", products=products)


@sales_bp.route("/<int:sale_id>/receipt")
@login_required
def receipt(sale_id):
    sale = sale_repo.get_sale_by_id(sale_id)
    if not sale:
        flash("Sale receipt not found.", "danger")
        return redirect(url_for("sales.list_sales"))
    return render_template("sales/receipt.html", sale=sale)
