from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.decorators import admin_required
from app.models import Supplier

suppliers_bp = Blueprint("suppliers", __name__)


@suppliers_bp.route("/")
@login_required
def list_suppliers():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template("suppliers/list.html", suppliers=suppliers)


def _apply_form(supplier):
    supplier.name = request.form.get("name", "").strip()
    supplier.phone = request.form.get("phone", "").strip()
    supplier.email = request.form.get("email", "").strip()
    supplier.address = request.form.get("address", "").strip()
    if not supplier.name:
        raise ValueError("Supplier name is required.")


@suppliers_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_supplier():
    if request.method == "POST":
        supplier = Supplier()
        try:
            _apply_form(supplier)
            db.session.add(supplier)
            db.session.commit()
            flash("Supplier added successfully.", "success")
            return redirect(url_for("suppliers.list_suppliers"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("suppliers/form.html", supplier=None)


@suppliers_bp.route("/<int:supplier_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_supplier(supplier_id):
    supplier = db.get_or_404(Supplier, supplier_id)
    if request.method == "POST":
        try:
            _apply_form(supplier)
            db.session.commit()
            flash("Supplier updated successfully.", "success")
            return redirect(url_for("suppliers.list_suppliers"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("suppliers/form.html", supplier=supplier)
