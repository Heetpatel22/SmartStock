"""
Authentication API endpoints for Postman testing.
"""

from flask import jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app.api import api_bp
from app.models import User


@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form.to_dict()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)
    return jsonify({
        "message": "Authentication successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin,
        },
    }), 200


@api_bp.route("/auth/me", methods=["GET"])
@login_required
def api_me():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_admin": current_user.is_admin,
    }), 200


@api_bp.route("/auth/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
