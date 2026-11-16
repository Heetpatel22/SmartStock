"""SCRUM-24 regression checks using the real routes and temporary SQLite DB."""

from decimal import Decimal

import pytest

from app import db
from app.core.exceptions import ValidationError
from app.models import Product, StockMovement, Supplier, User
from app.services.product_service import ProductService


def product_id(app):
    with app.app_context():
        return Product.query.filter_by(sku="TEST-001").one().id


@pytest.mark.parametrize("method", ["put", "patch"])
@pytest.mark.parametrize("quantity,direction,amount", [(12, "IN", 2), (7, "OUT", 3)])
def test_update_persists_details_and_one_stock_movement(app, client, login, method, quantity, direction, amount):
    login()
    pid = product_id(app)
    response = getattr(client, method)(f"/api/products/{pid}", json={
        "sku": " updated-001 ", "name": " Updated name ",
        "description": " Revised details ", "cost_price": "7.25",
        "selling_price": "14.50", "quantity": quantity, "reorder_level": 3,
    })
    assert response.status_code == 200
    with app.app_context():
        db.session.remove()
        product = db.session.get(Product, pid)
        assert (product.sku, product.name, product.description) == (
            "UPDATED-001", "Updated name", "Revised details")
        assert (product.cost_price, product.selling_price) == (Decimal("7.25"), Decimal("14.50"))
        assert (product.quantity, product.reorder_level) == (quantity, 3)
        movement = StockMovement.query.filter_by(product_id=pid).one()
        assert (movement.movement_type, movement.quantity) == (direction, amount)


@pytest.mark.parametrize("invalid", [
    {"sku": None}, {"name": []}, {"description": 123},
    {"quantity": None}, {"quantity": 1.5}, {"quantity": True},
    {"quantity": -1}, {"reorder_level": 2.5},
    {"cost_price": "Infinity"}, {"selling_price": "NaN"},
    {"selling_price": 0}, {"cost_price": -1},
    {"category_id": 99999}, {"supplier_id": 99999},
    {"category_id": "bad"}, {"supplier_id": 1.5},
])
def test_invalid_update_returns_400_and_preserves_saved_data(app, client, login, invalid):
    login()
    pid = product_id(app)
    response = client.patch(f"/api/products/{pid}", json={"name": "Must not persist", **invalid})
    assert response.status_code == 400
    assert "error" in response.get_json()
    with app.app_context():
        db.session.remove()
        product = db.session.get(Product, pid)
        assert (product.name, product.quantity, product.category_id) == ("Test Product", 10, 1)
        assert product.supplier_id is None
        assert StockMovement.query.filter_by(product_id=pid).count() == 0


def test_rejected_update_does_not_leak_mutations_on_later_commit(app):
    with app.app_context():
        product = Product.query.filter_by(sku="TEST-001").one()
        pid = product.id
        with pytest.raises(ValidationError):
            ProductService().update_product(pid, {"name": "Leaked name", "quantity": -1})
        # A caller may continue using the session after a validation error.
        db.session.commit()
        db.session.remove()
        assert db.session.get(Product, pid).name == "Test Product"


def test_failed_update_commit_rolls_back_product_and_movement(app, monkeypatch):
    from app.repositories.product_repository import ProductRepository
    with app.app_context():
        pid = Product.query.filter_by(sku="TEST-001").one().id
        repository = ProductRepository()
        def fail_commit():
            raise RuntimeError("Simulated commit failure")
        monkeypatch.setattr(repository, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="Simulated commit failure"):
            ProductService(product_repo=repository).update_product(pid, {"name": "Unsaved", "quantity": 20})
        db.session.remove()
        product = db.session.get(Product, pid)
        assert (product.name, product.quantity) == ("Test Product", 10)
        assert StockMovement.query.filter_by(product_id=pid).count() == 0


@pytest.mark.parametrize("body", [[{"name": "bad"}], "bad", None])
def test_update_rejects_non_object_json(app, client, login, body):
    import json
    login()
    response = client.patch(f"/api/products/{product_id(app)}",
                            data=json.dumps(body), content_type="application/json")
    assert response.status_code == 400


def test_update_rejects_malformed_json(app, client, login):
    login()
    response = client.patch(f"/api/products/{product_id(app)}",
                            data='{"name":', content_type="application/json")
    assert response.status_code == 400


def test_duplicate_sku_returns_409_without_changing_product(app, client, login):
    login()
    with app.app_context():
        db.session.add(Product(sku="OTHER", name="Other", cost_price=1, selling_price=2))
        db.session.commit()
    pid = product_id(app)
    assert client.patch(f"/api/products/{pid}", json={"sku": " other "}).status_code == 409
    with app.app_context():
        assert db.session.get(Product, pid).sku == "TEST-001"


def test_update_associations_then_clear_them(app, client, login):
    login()
    with app.app_context():
        supplier = Supplier(name="Test Supplier")
        db.session.add(supplier)
        db.session.commit()
        sid = supplier.id
    pid = product_id(app)
    assert client.patch(f"/api/products/{pid}", json={"supplier_id": sid}).status_code == 200
    with app.app_context():
        assert db.session.get(Product, pid).supplier_id == sid
    assert client.patch(f"/api/products/{pid}", json={"supplier_id": None, "category_id": ""}).status_code == 200
    with app.app_context():
        product = db.session.get(Product, pid)
        assert product.supplier_id is None and product.category_id is None


def test_update_missing_product_returns_404(client, login):
    login()
    assert client.patch("/api/products/99999", json={"name": "Missing"}).status_code == 404
    assert client.post("/products/99999/edit", data={"name": "Missing"}).status_code == 302


def test_update_api_requires_authentication(app, client):
    response = client.patch(f"/api/products/{product_id(app)}", json={"name": "Denied"})
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_cashier_cannot_edit_via_api_or_form(app, client, login):
    with app.app_context():
        cashier = User(name="Cashier", email="cashier@example.com", role="cashier")
        cashier.set_password("Password123!")
        db.session.add(cashier)
        db.session.commit()
    login("cashier@example.com")
    pid = product_id(app)
    assert client.patch(f"/api/products/{pid}", json={"name": "Denied"}).status_code == 403
    assert client.post(f"/products/{pid}/edit", data={"name": "Denied"}).status_code == 403
    with app.app_context():
        assert db.session.get(Product, pid).name == "Test Product"


def test_html_edit_saves_valid_values_and_rejects_invalid_values(app, client, login):
    login()
    pid = product_id(app)
    assert client.get(f"/products/{pid}/edit").status_code == 200
    fields = {"sku": "TEST-001", "name": "Form update", "cost_price": "5",
              "selling_price": "12", "quantity": "10", "reorder_level": "2"}
    response = client.post(f"/products/{pid}/edit", data=fields, follow_redirects=True)
    assert b"Product updated successfully" in response.data
    response = client.post(f"/products/{pid}/edit", data={**fields, "quantity": "-1"}, follow_redirects=True)
    assert b"Quantity must be a non-negative whole number" in response.data
    with app.app_context():
        product = db.session.get(Product, pid)
        assert (product.name, product.quantity, product.selling_price) == ("Form update", 10, Decimal("12"))
