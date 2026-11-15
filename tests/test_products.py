from app.models import Product


def test_admin_can_add_product(app, client, login):
    login()
    response = client.post(
        "/products/add",
        data={
            "sku": "NEW-001",
            "name": "New Product",
            "description": "Test",
            "cost_price": "12.50",
            "selling_price": "20.00",
            "quantity": "5",
            "reorder_level": "2",
            "category_id": "",
            "supplier_id": "",
        },
        follow_redirects=True,
    )
    assert b"Product added successfully" in response.data
    with app.app_context():
        assert Product.query.filter_by(sku="NEW-001").first() is not None


def test_stock_cannot_be_adjusted_below_zero(app, client, login):
    login()
    with app.app_context():
        product_id = Product.query.filter_by(sku="TEST-001").first().id
    response = client.post(
        f"/products/{product_id}/adjust",
        data={"quantity_change": "-50", "reason": "Damage"},
        follow_redirects=True,
    )
    assert b"Stock cannot fall below zero" in response.data


def test_stock_adjustment_persists_in_database(app, client, login):
    login()
    with app.app_context():
        product = Product.query.filter_by(sku="TEST-001").first()
        initial_qty = product.quantity
        product_id = product.id

    response = client.post(
        f"/products/{product_id}/adjust",
        data={"quantity_change": "15", "reason": "Supplier restocking"},
        follow_redirects=True,
    )
    assert b"Stock adjusted successfully" in response.data

    with app.app_context():
        from app import db
        updated_product = db.session.get(Product, product_id)
        assert updated_product.quantity == initial_qty + 15

