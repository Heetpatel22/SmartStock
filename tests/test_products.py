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
