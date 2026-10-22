# SmartStock Inventory and Sales Management System

SmartStock is a Flask web application for small businesses to manage products, suppliers, stock movements, sales, receipts, and summary reports.

## Included features

- User registration, login, logout, and role-based administration
- Product and category management through the web interface
- Supplier management
- Stock increases, reductions, and movement history
- Sales checkout with automatic stock deduction
- Printable receipt page
- Sales history and dashboard metrics
- Unit and integration tests with Pytest
- GitHub Actions CI workflow
- Modular Flask blueprints, service layer, and repository-style data access

## Technology stack

- Python and Flask
- Flask-SQLAlchemy with SQLite
- Flask-Login
- Bootstrap 5
- Pytest
- GitHub Actions

## Fastest Windows setup

Double-click `setup_and_run.bat`, or use the manual PowerShell steps below.

## Run on Windows PowerShell

```powershell
cd SmartStock
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

The first account registered becomes the administrator. Later accounts are created as cashiers.

## Add demonstration data

After activating the virtual environment:

```powershell
$env:FLASK_APP="run.py"
flask seed-demo
```

Demo login:

- Email: `admin@smartstock.local`
- Password: `Admin123!`

## Run tests

```powershell
pytest
```

## Main modules

- `app/auth`: authentication and user sessions
- `app/products`: products, categories, and stock adjustment
- `app/suppliers`: supplier records
- `app/sales`: checkout, sales history, and receipts
- `app/services`: business rules for inventory and sales
- `app/models.py`: database entities

## Suggested next development phases

1. Add PDF receipt downloads.
2. Add CSV and Excel report exports.
3. Add barcode scanning.
4. Add purchase orders and supplier deliveries.
5. Add charts and date-filtered reports.
6. Deploy to Render using PostgreSQL.
