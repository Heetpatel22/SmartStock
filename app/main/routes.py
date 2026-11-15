"""
Main dashboard route (Presentation Layer).
Adheres to SRP by delegating metrics computation to DashboardService.
"""

from flask import Blueprint, render_template
from flask_login import login_required
from app.services.dashboard_service import DashboardService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    metrics = DashboardService.get_metrics()
    return render_template("main/dashboard.html", **metrics)
