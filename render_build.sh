#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=============================================="
echo "  [Render Build] Installing dependencies..."
echo "=============================================="

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "=============================================="
echo "  [Render Build] Initializing database & demo data..."
echo "=============================================="

export FLASK_APP=run.py
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
flask seed-demo || echo "Demo seed completed or skipped."

echo "=============================================="
echo "  [Render Build] Build completed successfully!"
echo "=============================================="
