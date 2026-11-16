"""
Product REST API endpoints for Postman testing.
Implements the 4 User Stories via ProductService (SRP & DIP):
- US-01 (SCRUM-22): Add New Product
- US-02 (SCRUM-23): View Product Inventory
- US-03 (SCRUM-24): Update Product Details
- US-04 (SCRUM-25): Delete Product
"""

from flask import jsonify, request
from flask_login import current_user, login_required

from app.api import api_bp
from app.core.exceptions import ValidationError
from app.models import Product
from app.services.product_service import ProductService

product_service = ProductService()


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
    products = product_service.get_catalog(search=search)
    return jsonify({
        "total": len(products),
        "products": [_serialize_product(p) for p in products],
    }), 200


@api_bp.route("/products/<int:product_id>", methods=["GET"])
@login_required
def api_get_product(product_id):
    product = product_service.get_by_id(product_id)
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
    try:
        product = product_service.create_product(
            sku=data.get("sku", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            cost_price=data.get("cost_price", "0"),
            selling_price=data.get("selling_price", "0"),
            quantity=data.get("quantity", 0),
            reorder_level=data.get("reorder_level", 5),
            category_id=int(data["category_id"]) if data.get("category_id") else None,
            supplier_id=int(data["supplier_id"]) if data.get("supplier_id") else None,
        )
        return jsonify({
            "message": "Product created successfully",
            "product": _serialize_product(product),
        }), 201
    except ValidationError as exc:
        status_code = 409 if "already in use" in str(exc) else 400
        return jsonify({"error": str(exc)}), status_code


# -------------------------------------------------------------
# US-03 (SCRUM-24): Update Product Details
# -------------------------------------------------------------
@api_bp.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def api_update_product(product_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    if not current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    if not product_service.get_by_id(product_id):
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True) if request.is_json else request.form.to_dict()
    if not isinstance(data, dict):
        return jsonify({"error": "Product updates must be a JSON object"}), 400
    try:
        updated = product_service.update_product(product_id, data)
        return jsonify({
            "message": "Product updated successfully",
            "product": _serialize_product(updated),
        }), 200
    except ValidationError as exc:
        status_code = 409 if "already in use" in str(exc) else 400
        return jsonify({"error": str(exc)}), status_code


# -------------------------------------------------------------
# US-04 (SCRUM-25): Delete Product
# -------------------------------------------------------------
@api_bp.route("/products/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    if not current_user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403

    if not product_service.get_by_id(product_id):
        return jsonify({"error": "Product not found"}), 404

    try:
        product_service.delete_product(product_id)
        return jsonify({
            "message": "Product deleted successfully",
            "id": product_id,
        }), 200
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400
