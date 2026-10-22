import click
from flask.cli import with_appcontext

from app import db
from app.models import Category, Product, Supplier, User


def register_commands(app):
    @app.cli.command("seed-demo")
    @with_appcontext
    def seed_demo():
        if User.query.filter_by(email="admin@smartstock.local").first():
            click.echo("Demo data already exists.")
            return

        admin = User(name="Demo Admin", email="admin@smartstock.local", role="admin")
        admin.set_password("Admin123!")

        electronics = Category(name="Electronics")
        accessories = Category(name="Accessories")
        supplier = Supplier(
            name="Metro Wholesale",
            phone="+1 555 0100",
            email="sales@metrowholesale.example",
            address="100 Market Street",
        )

        products = [
            Product(
                sku="KB-001",
                name="Wireless Keyboard",
                cost_price=18,
                selling_price=29.99,
                quantity=20,
                reorder_level=5,
                category=accessories,
                supplier=supplier,
            ),
            Product(
                sku="MS-001",
                name="Optical Mouse",
                cost_price=8,
                selling_price=14.99,
                quantity=30,
                reorder_level=8,
                category=accessories,
                supplier=supplier,
            ),
            Product(
                sku="SP-001",
                name="Portable Speaker",
                cost_price=22,
                selling_price=39.99,
                quantity=10,
                reorder_level=3,
                category=electronics,
                supplier=supplier,
            ),
        ]

        db.session.add_all([admin, electronics, accessories, supplier, *products])
        db.session.commit()
        click.echo("Demo data created. Login: admin@smartstock.local / Admin123!")
