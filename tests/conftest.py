import pytest

from app import create_app, db
from app.models import Category, Product, User


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(name="Test Admin", email="admin@example.com", role="admin")
        admin.set_password("Password123!")
        category = Category(name="Test Category")
        product = Product(
            sku="TEST-001",
            name="Test Product",
            cost_price=5,
            selling_price=10,
            quantity=10,
            reorder_level=2,
            category=category,
        )
        db.session.add_all([admin, category, product])
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def do_login(email="admin@example.com", password="Password123!"):
        return client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    return do_login
