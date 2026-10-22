from app import db
from app.models import Product, Sale


def test_sale_reduces_stock_and_calculates_total(app, client, login):
    login()
    with app.app_context():
        product = Product.query.filter_by(sku="TEST-001").first()
        product_id = product.id

    response = client.post(
        "/sales/new",
        data={f"qty_{product_id}": "3", "payment_method": "cash"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Thank you for your purchase" in response.data

    with app.app_context():
        product = db.session.get(Product, product_id)
        sale = Sale.query.one()
        assert product.quantity == 7
        assert float(sale.total) == 30.00


def test_sale_rejects_quantity_above_stock(app, client, login):
    login()
    with app.app_context():
        product_id = Product.query.filter_by(sku="TEST-001").first().id

    response = client.post(
        "/sales/new",
        data={f"qty_{product_id}": "50", "payment_method": "cash"},
        follow_redirects=True,
    )
    assert b"Insufficient stock" in response.data
