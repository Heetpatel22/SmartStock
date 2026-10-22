from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app import db
from app.decorators import admin_required
from app.models import Category, Product, StockMovement, Supplier
from app.services.inventory_service import InventoryError, InventoryService

products_bp = Blueprint("products", __name__)


@products_bp.route("/")
@login_required
def list_products():
    search = request.args.get("q", "").strip()
    query = Product.query
    if search:
        query = query.filter(or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%")))
    products = query.order_by(Product.name).all()
    return render_template("products/list.html", products=products, search=search)


def _form_data(product=None):
    return {
        "categories": Category.query.order_by(Category.name).all(),
        "suppliers": Supplier.query.order_by(Supplier.name).all(),
        "product": product,
    }


def _apply_product_form(product):
    product.sku = request.form.get("sku", "").strip().upper()
    product.name = request.form.get("name", "").strip()
    product.description = request.form.get("description", "").strip()
    product.cost_price = Decimal(request.form.get("cost_price", "0"))
    product.selling_price = Decimal(request.form.get("selling_price", "0"))
    product.quantity = int(request.form.get("quantity", "0"))
    product.reorder_level = int(request.form.get("reorder_level", "5"))
    product.category_id = int(request.form["category_id"]) if request.form.get("category_id") else None
    product.supplier_id = int(request.form["supplier_id"]) if request.form.get("supplier_id") else None

    if not product.sku or not product.name:
        raise ValueError("SKU and product name are required.")
    if product.cost_price < 0 or product.selling_price <= 0:
        raise ValueError("Prices must be valid positive amounts.")
    if product.quantity < 0 or product.reorder_level < 0:
        raise ValueError("Stock quantities cannot be negative.")


@products_bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Category name is required.", "danger")
        elif Category.query.filter(Category.name.ilike(name)).first():
            flash("That category already exists.", "danger")
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash("Category added successfully.", "success")
        return redirect(url_for("products.categories"))

    category_list = Category.query.order_by(Category.name).all()
    return render_template("products/categories.html", categories=category_list)


@products_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    category = db.get_or_404(Category, category_id)
    if category.products:
        flash("A category assigned to products cannot be deleted.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted.", "success")
    return redirect(url_for("products.categories"))


@products_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        product = Product()
        try:
            _apply_product_form(product)
            if Product.query.filter_by(sku=product.sku).first():
                raise ValueError("That SKU is already in use.")
            db.session.add(product)
            db.session.flush()
            if product.quantity:
                db.session.add(StockMovement(product=product, movement_type="IN", quantity=product.quantity, reason="Opening stock"))
            db.session.commit()
            flash("Product added successfully.", "success")
            return redirect(url_for("products.list_products"))
        except (ValueError, InvalidOperation) as exc:
            db.session.rollback()
            flash(str(exc), "danger")

    return render_template("products/form.html", **_form_data())


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    if request.method == "POST":
        original_quantity = product.quantity
        try:
            _apply_product_form(product)
            duplicate = Product.query.filter(Product.sku == product.sku, Product.id != product.id).first()
            if duplicate:
                raise ValueError("That SKU is already in use.")
            difference = product.quantity - original_quantity
            if difference:
                db.session.add(StockMovement(product=product, movement_type="IN" if difference > 0 else "OUT", quantity=abs(difference), reason="Product edit"))
            db.session.commit()
            flash("Product updated successfully.", "success")
            return redirect(url_for("products.list_products"))
        except (ValueError, InvalidOperation) as exc:
            db.session.rollback()
            flash(str(exc), "danger")

    return render_template("products/form.html", **_form_data(product))


@products_bp.route("/<int:product_id>/adjust", methods=["GET", "POST"])
@login_required
@admin_required
def adjust_stock(product_id):
    product = db.get_or_404(Product, product_id)
    if request.method == "POST":
        try:
            quantity_change = int(request.form.get("quantity_change", "0"))
            if quantity_change == 0:
                raise InventoryError("Enter a non-zero adjustment.")
            InventoryService.adjust_stock(product, quantity_change, request.form.get("reason", ""))
            db.session.commit()
            flash("Stock adjusted successfully.", "success")
            return redirect(url_for("products.list_products"))
        except (ValueError, InventoryError) as exc:
            db.session.rollback()
            flash(str(exc), "danger")

    movements = StockMovement.query.filter_by(product_id=product.id).order_by(StockMovement.created_at.desc()).limit(10).all()
    return render_template("products/adjust.html", product=product, movements=movements)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    if product.sale_items:
        flash("Products with recorded sales cannot be deleted.", "danger")
    else:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted.", "success")
    return redirect(url_for("products.list_products"))
