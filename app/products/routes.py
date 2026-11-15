"""
Product and Category routes (Presentation Layer).
Adheres to Single Responsibility Principle (SRP) by delegating business logic
and persistence to ProductService, CategoryRepository, and SupplierRepository.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.exceptions import ValidationError
from app.decorators import admin_required
from app.repositories.category_repository import CategoryRepository
from app.repositories.supplier_repository import SupplierRepository
from app.services.inventory_service import InventoryError, InventoryService
from app.services.product_service import ProductService

products_bp = Blueprint("products", __name__)
product_service = ProductService()
category_repo = CategoryRepository()
supplier_repo = SupplierRepository()


@products_bp.route("/")
@login_required
def list_products():
    search = request.args.get("q", "").strip()
    products = product_service.get_catalog(search=search)
    return render_template("products/list.html", products=products, search=search)


def _form_data(product=None):
    return {
        "categories": category_repo.get_all(),
        "suppliers": supplier_repo.get_all(),
        "product": product,
    }


@products_bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            product_service.create_category(name)
            flash("Category added successfully.", "success")
        except ValidationError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("products.categories"))

    return render_template("products/categories.html", categories=category_repo.get_all())


@products_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    try:
        product_service.delete_category(category_id)
        flash("Category deleted.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("products.categories"))


@products_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        try:
            product_service.create_product(
                sku=request.form.get("sku", ""),
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                cost_price=request.form.get("cost_price", "0"),
                selling_price=request.form.get("selling_price", "0"),
                quantity=request.form.get("quantity", "0"),
                reorder_level=request.form.get("reorder_level", "5"),
                category_id=int(request.form["category_id"]) if request.form.get("category_id") else None,
                supplier_id=int(request.form["supplier_id"]) if request.form.get("supplier_id") else None,
            )
            flash("Product added successfully.", "success")
            return redirect(url_for("products.list_products"))
        except (ValidationError, ValueError) as exc:
            flash(str(exc), "danger")

    return render_template("products/form.html", **_form_data())


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    product = product_service.get_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        try:
            updates = {
                "sku": request.form.get("sku", ""),
                "name": request.form.get("name", ""),
                "description": request.form.get("description", ""),
                "cost_price": request.form.get("cost_price", "0"),
                "selling_price": request.form.get("selling_price", "0"),
                "quantity": request.form.get("quantity", "0"),
                "reorder_level": request.form.get("reorder_level", "5"),
                "category_id": request.form.get("category_id"),
                "supplier_id": request.form.get("supplier_id"),
            }
            product_service.update_product(product_id, updates)
            flash("Product updated successfully.", "success")
            return redirect(url_for("products.list_products"))
        except (ValidationError, ValueError) as exc:
            flash(str(exc), "danger")

    return render_template("products/form.html", **_form_data(product))


@products_bp.route("/<int:product_id>/adjust", methods=["GET", "POST"])
@login_required
@admin_required
def adjust_stock(product_id):
    product = product_service.get_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        try:
            quantity_change = int(request.form.get("quantity_change", "0"))
            InventoryService.adjust_stock(product, quantity_change, request.form.get("reason", ""))
            flash("Stock adjusted successfully.", "success")
            return redirect(url_for("products.list_products"))
        except (ValueError, InventoryError) as exc:
            flash(str(exc), "danger")

    movements = product_service.movement_recorder.get_by_product_id(product_id, limit=10)
    return render_template("products/adjust.html", product=product, movements=movements)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_product(product_id):
    try:
        product_service.delete_product(product_id)
        flash("Product deleted.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("products.list_products"))
