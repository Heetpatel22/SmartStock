"""SCRUM-25 authorization, safeguard and cascade checks against SQLite."""

import pytest

from app import db
from app.models import Product, Sale, SaleItem, StockMovement, User


def product_id(app):
    with app.app_context():
        return Product.query.filter_by(sku="TEST-001").one().id


def test_delete_api_requires_authentication_and_preserves_product(app, client):
    pid = product_id(app)
    response = client.delete(f"/api/products/{pid}")
    assert response.status_code == 401
    assert "error" in response.get_json()
    with app.app_context():
        assert db.session.get(Product, pid) is not None


def test_cashier_cannot_delete_via_api_or_form(app, client, login):
    with app.app_context():
        cashier = User(name="Cashier", email="cashier@example.com", role="cashier")
        cashier.set_password("Password123!")
        db.session.add(cashier)
        db.session.commit()
    login("cashier@example.com")
    pid = product_id(app)
    response = client.delete(f"/api/products/{pid}")
    assert response.status_code == 403
    assert response.get_json()["error"] == "Admin privileges required"
    assert client.post(f"/products/{pid}/delete").status_code == 403
    with app.app_context():
        assert db.session.get(Product, pid) is not None


@pytest.mark.parametrize("via_form", [False, True])
def test_delete_removes_eligible_product_and_stock_history(app, client, login, via_form):
    login()
    pid = product_id(app)
    with app.app_context():
        db.session.add(StockMovement(product_id=pid, movement_type="IN", quantity=10, reason="Opening stock"))
        db.session.commit()
    if via_form:
        response = client.post(f"/products/{pid}/delete", follow_redirects=True)
        assert b"Product deleted" in response.data
    else:
        response = client.delete(f"/api/products/{pid}")
        assert response.status_code == 200
        assert response.get_json()["id"] == pid
    with app.app_context():
        db.session.remove()
        assert db.session.get(Product, pid) is None
        assert StockMovement.query.filter_by(product_id=pid).count() == 0
    assert client.get(f"/api/products/{pid}").status_code == 404
    assert client.delete(f"/api/products/{pid}").status_code == 404


@pytest.mark.parametrize("via_form", [False, True])
def test_product_with_sales_cannot_be_deleted(app, client, login, via_form):
    login()
    pid = product_id(app)
    with app.app_context():
        admin = User.query.filter_by(email="admin@example.com").one()
        sale = Sale(receipt_number="DELETE-GUARD", user_id=admin.id, total=10)
        sale.items.append(SaleItem(product_id=pid, quantity=1, unit_price=10, subtotal=10))
        db.session.add_all([sale, StockMovement(product_id=pid, movement_type="OUT", quantity=1, reason="Sale")])
        db.session.commit()
    if via_form:
        response = client.post(f"/products/{pid}/delete", follow_redirects=True)
        assert b"Products with recorded sales cannot be deleted" in response.data
    else:
        response = client.delete(f"/api/products/{pid}")
        assert response.status_code == 400
        assert "recorded sales" in response.get_json()["error"]
    with app.app_context():
        db.session.remove()
        assert db.session.get(Product, pid) is not None
        assert SaleItem.query.filter_by(product_id=pid).count() == 1
        assert StockMovement.query.filter_by(product_id=pid).count() == 1


def test_delete_missing_id_returns_404(client, login):
    login()
    response = client.delete("/api/products/99999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_browser_delete_requires_login_and_post(app, client, login):
    pid = product_id(app)
    assert client.post(f"/products/{pid}/delete").status_code == 302
    login()
    assert client.get(f"/products/{pid}/delete").status_code == 405
    with app.app_context():
        assert db.session.get(Product, pid) is not None
