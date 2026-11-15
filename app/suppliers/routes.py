"""
Supplier routes (Presentation Layer).
Adheres to SRP by delegating supplier domain logic to SupplierService.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.core.exceptions import ValidationError
from app.decorators import admin_required
from app.services.supplier_service import SupplierService

suppliers_bp = Blueprint("suppliers", __name__)
supplier_service = SupplierService()


@suppliers_bp.route("/")
@login_required
def list_suppliers():
    suppliers = supplier_service.get_all()
    return render_template("suppliers/list.html", suppliers=suppliers)


@suppliers_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_supplier():
    if request.method == "POST":
        try:
            supplier_service.create_supplier(
                name=request.form.get("name", ""),
                phone=request.form.get("phone", ""),
                email=request.form.get("email", ""),
                address=request.form.get("address", ""),
            )
            flash("Supplier added successfully.", "success")
            return redirect(url_for("suppliers.list_suppliers"))
        except ValidationError as exc:
            flash(str(exc), "danger")

    return render_template("suppliers/form.html", supplier=None)


@suppliers_bp.route("/<int:supplier_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_supplier(supplier_id):
    supplier = supplier_service.get_by_id(supplier_id)
    if not supplier:
        flash("Supplier not found.", "danger")
        return redirect(url_for("suppliers.list_suppliers"))

    if request.method == "POST":
        try:
            supplier_service.update_supplier(
                supplier_id=supplier_id,
                name=request.form.get("name", ""),
                phone=request.form.get("phone", ""),
                email=request.form.get("email", ""),
                address=request.form.get("address", ""),
            )
            flash("Supplier updated successfully.", "success")
            return redirect(url_for("suppliers.list_suppliers"))
        except ValidationError as exc:
            flash(str(exc), "danger")

    return render_template("suppliers/form.html", supplier=supplier)
