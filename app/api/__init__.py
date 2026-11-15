"""
REST API Blueprint package for SmartStock.
Supports Postman functional testing for user stories and automated API pipelines.
"""

from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from app.api import auth, products  # noqa: E402, F401

