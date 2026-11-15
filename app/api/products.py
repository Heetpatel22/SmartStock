"""
Product REST API endpoints for Postman testing.
Implements the 4 User Stories:
- US-01 (SCRUM-22): Add New Product
- US-02 (SCRUM-23): View Product Inventory
- US-03 (SCRUM-24): Update Product Details
- US-04 (SCRUM-25): Delete Product
"""

from decimal import Decimal, InvalidOperation
from flask import jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.api import api_bp
from app.models import Category, Product, StockMovement, Supplier


def _serialize_product(p: Product) -> dict:
    return {
        "id": p.id,
        "sku": p.sku,
        "name": p.name,
        "description": p.description or "",
        "cost_price": float(p.cost_price),
        "selling_price": float(p.selling_price),
        "formatted_price": f"₹{float(p.selling_price):,.2f}",
        "quantity": p.quantity,
        "reorder_level": p.reorder_level,
        "is_low_stock": p.is_low_stock,
        "category": p.category.name if p.category else None,
        "category_id": p.category_id,
        "supplier": p.supplier.name if p.supplier else None,
        "supplier_id": p.supplier_id,
    }


# -------------------------------------------------------------
# US-02 (SCRUM-23): View Product Inventory
# -------------------------------------------------------------
@api_bp.route("/products", methods=["GET"])
@login_required
def api_list_products():
    search = request.args.get("q", "").strip()
    query = Product.query
    if search:
        query = query.filter(
            or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%"))
        )
    products = query.order_by(Product.name).all()
    return jsonify({
        "total": len(products),
        "products": [_serialize_product(p) for p in products],
    }), 200


@api_bp.route("/products/<int:product_id>", methods=["GET"])
@login_required
def api_get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(_serialize_product(product)), 200


# -------------------------------------------------------------
# US-01 (SCRUM-22): Add New Product
# -------------------------------------------------------------
@api_bp.route("/products", methods=["POST"])
@login_required
def api_add_product():
    if not current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    data = request.get_json(silent=True) or request.form.to_dict()
    sku = (data.get("sku") or "").strip().upper()
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()

    if not sku or not name:
        return jsonify({"error": "SKU and product name are required"}), 400

    if Product.query.filter_by(sku=sku).first():
        return jsonify({"error": f"SKU '{sku}' already exists"}), 409

    try:
        cost_price = Decimal(str(data.get("cost_price", "0")))
        selling_price = Decimal(str(data.get("selling_price", "0")))
        quantity = int(data.get("quantity", 0))
        reorder_level = int(data.get("reorder_level", 5))

        if cost_price < 0 or selling_price <= 0:
            return jsonify({"error": "Prices must be positive numbers"}), 400
        if quantity < 0 or reorder_level < 0:
            return jsonify({"error": "Quantities cannot be negative"}), 400
    except (ValueError, InvalidOperation):
        return jsonify({"error": "Invalid numerical values supplied"}), 400

    product = Product(
        sku=sku,
        name=name,
        description=description,
        cost_price=cost_price,
        selling_price=selling_price,
        quantity=quantity,
        reorder_level=reorder_level,
        category_id=int(data["category_id"]) if data.get("category_id") else None,
        supplier_id=int(data["supplier_id"]) if data.get("supplier_id") else None,
    )
    db.session.add(product)
    db.session.flush()

    if quantity > 0:
        movement = StockMovement(
            product_id=product.id,
            movement_type="IN",
            quantity=quantity,
            reason="Opening stock via API",
        )
        db.session.add(movement)

    db.session.commit()
    return jsonify({
        "message": "Product created successfully",
        "product": _serialize_product(product),
    }), 201


# -------------------------------------------------------------
# US-03 (SCRUM-24): Update Product Details
# -------------------------------------------------------------
@api_bp.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
@login_required
def api_update_product(product_id):
    if not current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True) or request.form.to_dict()
    original_quantity = product.quantity

    if "name" in data:
        product.name = data["name"].strip()
    if "description" in data:
        product.description = data["description"].strip()
    if "sku" in data:
        new_sku = data["sku"].strip().upper()
        duplicate = Product.query.filter(Product.sku == new_sku, Product.id != product.id).first()
        if duplicate:
            return jsonify({"error": f"SKU '{new_sku}' is already in use by another product"}), 409
        product.sku = new_sku

    try:
        if "cost_price" in data:
            cp = Decimal(str(data["cost_price"]))
            if cp < 0:
                return jsonify({"error": "Cost price cannot be negative"}), 400
            product.cost_price = cp

        if "selling_price" in data:
            sp = Decimal(str(data["selling_price"]))
            if sp <= 0:
                return jsonify({"error": "Selling price must be positive"}), 400
            product.selling_price = sp

        if "reorder_level" in data:
            rl = int(data["reorder_level"])
            if rl < 0:
                return jsonify({"error": "Reorder level cannot be negative"}), 400
            product.reorder_level = rl

        if "quantity" in data:
            qty = int(data["quantity"])
            if qty < 0:
                return jsonify({"error": "Quantity cannot be negative"}), 400
            difference = qty - original_quantity
            if difference != 0:
                product.quantity = qty
                movement = StockMovement(
                    product_id=product.id,
                    movement_type="IN" if difference > 0 else "OUT",
                    quantity=abs(difference),
                    reason="Product update via API",
                )
                db.session.add(movement)
    except (ValueError, InvalidOperation):
        return jsonify({"error": "Invalid numerical values supplied"}), 400

    db.session.commit()
    return jsonify({
        "message": "Product updated successfully",
        "product": _serialize_product(product),
    }), 200


# -------------------------------------------------------------
# US-04 (SCRUM-25): Delete Product
# -------------------------------------------------------------
@api_bp.route("/products/<int:product_id>", methods=["DELETE"])
@login_required
def api_delete_product(product_id):
    if not current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Safeguard (SCRUM-49): Do not delete product with recorded sales
    if product.sale_items:
        return jsonify({
            "error": "Products with existing recorded sales cannot be deleted to preserve accounting integrity."
        }), 400

    db.session.delete(product)
    db.session.commit()
    return jsonify({
        "message": "Product deleted successfully",
        "id": product_id,
    }), 200

