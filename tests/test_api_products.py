"""
Functional API tests for the 4 User Stories:
- US-01 (SCRUM-22): Add New Product
- US-02 (SCRUM-23): View Product Inventory
- US-03 (SCRUM-24): Update Product Details
- US-04 (SCRUM-25): Delete Product
"""

from app import db
from app.models import Product


def test_api_login(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Authentication successful"
    assert data["user"]["is_admin"] is True


def test_us01_add_new_product(client, login):
    login()
    payload = {
        "sku": "KB-RGB-01",
        "name": "Mechanical Keyboard RGB",
        "description": "Tactile Blue Switches",
        "cost_price": 2200.00,
        "selling_price": 3499.00,
        "quantity": 15,
        "reorder_level": 4,
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["product"]["sku"] == "KB-RGB-01"
    assert data["product"]["quantity"] == 15
    assert data["product"]["formatted_price"] == "₹3,499.00"


def test_us02_view_product_inventory(client, login):
    login()
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.get_json()
    assert "products" in data
    assert data["total"] >= 1
    assert any(p["sku"] == "TEST-001" for p in data["products"])


def test_us03_update_product_details(app, client, login):
    login()
    with app.app_context():
        product = Product.query.filter_by(sku="TEST-001").first()
        product_id = product.id

    update_payload = {
        "name": "Test Product Updated",
        "selling_price": 1499.00,
        "quantity": 20,
    }
    response = client.put(f"/api/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["product"]["name"] == "Test Product Updated"
    assert data["product"]["quantity"] == 20
    assert data["product"]["selling_price"] == 1499.00


def test_us04_delete_product(app, client, login):
    login()
    with app.app_context():
        product = Product.query.filter_by(sku="TEST-001").first()
        product_id = product.id

    response = client.delete(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Product deleted successfully"

    # Verify deleted
    with app.app_context():
        assert db.session.get(Product, product_id) is None
