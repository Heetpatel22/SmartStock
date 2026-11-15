# SmartStock Test Execution Report & Outcomes
**Course**: CSE706 - Agile Development of a Mini Software Product using Scrum Framework  
**Deliverable**: Step 3 & 4 - Comprehensive Test Scripts, Execution Logs & Reports  
**Framework**: Pytest (xUnit Architecture) & GitHub Actions Continuous Integration (CI)  
**Execution Timestamp**: 2026-11-15 17:20:42 IST  
**Environment**: Python 3.13.3 (Windows) & Python 3.12 (Ubuntu CI Runner)  

---

## 1. Executive Test Execution Summary

| Metric | Result | Status |
| :--- | :--- | :--- |
| **Total Test Cases** | **29** | `COLLECTED` |
| **Tests Passed** | **29** | `PASSED (100%)` |
| **Tests Failed** | **0** | `NONE` |
| **Tests Skipped / Errors** | **0** | `NONE` |
| **Warnings** | **0** | `CLEAN` |
| **Total Execution Time** | **14.80 seconds** | `OPTIMAL` |
| **GitHub Actions CI Status** | **✓ Passed (Green Checkmark)** | `LIVE ON GITHUB` |

---

## 2. Test Cases Breakdown & Outcomes

### Category A: Module 1 — Test-Driven Development (TDD) Inventory Service
**File**: `tests/test_solid_inventory.py` | **Principle**: Single Responsibility (SRP) & Dependency Inversion (DIP)

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 1 | `test_stock_increase_records_movement_in` | Adding stock increases `quantity` and creates an audit movement of type `IN`. | **PASSED** |
| 2 | `test_stock_decrease_records_movement_out` | Reducing stock decreases `quantity` and creates an audit movement of type `OUT`. | **PASSED** |
| 3 | `test_stock_cannot_fall_below_zero` | Domain invariant: Prevents stock reduction below zero, raising `InventoryError`. | **PASSED** |
| 4 | `test_zero_quantity_adjustment_rejected` | Domain validation: Rejects no-op zero adjustments, raising `InventoryError`. | **PASSED** |

---

### Category B: Module 2 — Test-Driven Development (TDD) Sales Service
**File**: `tests/test_solid_sales.py` | **Principle**: Open/Closed (OCP) & Dependency Inversion (DIP)

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 5 | `test_successful_checkout_calculates_total_and_deducts_stock` | Verifies multi-item subtotal calculation, grand total sum, stock deduction, and sequential receipt generation. | **PASSED** |
| 6 | `test_checkout_fails_when_requested_quantity_exceeds_stock` | Prevents checkout if requested quantity > available stock; preserves stock intact. | **PASSED** |
| 7 | `test_checkout_fails_on_unsupported_payment_method` | Strategy validation: Rejects unregistered payment methods, raising `PaymentError`. | **PASSED** |
| 8 | `test_checkout_supports_indian_upi_payment` | Strategy validation: Successfully processes Indian Rupee UPI payments (`GPay`, `PhonePe`, `Paytm`). | **PASSED** |

---

### Category C: Module 3 — Product Catalog Domain Service
**File**: `tests/test_solid_product_service.py` | **Principle**: Single Responsibility (SRP) & Dependency Inversion (DIP)

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 9 | `test_create_product_success_and_logs_opening_stock` | Validates product creation with SKU, pricing, and automated opening stock movement logging. | **PASSED** |
| 10 | `test_create_product_rejects_duplicate_sku` | Enforces global SKU uniqueness across warehouse items (`ValidationError`). | **PASSED** |
| 11 | `test_update_product_quantity_difference_logged` | Reconciles stock quantity changes during product edits and records audit logs. | **PASSED** |
| 12 | `test_delete_product_safeguards_against_items_with_sales` | Safeguard check: blocks deletion of products with recorded sales transactions. | **PASSED** |

---

### Category D: Open/Closed (OCP) & Liskov Substitution (LSP) Payment Strategies
**File**: `tests/test_payment_strategies.py` | **Pattern**: Strategy Pattern

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 13 | `test_cash_strategy_validation` | Validates cash payments and rejects negative amounts. | **PASSED** |
| 14 | `test_card_strategy_validation` | Validates card payments and enforces amounts > 0. | **PASSED** |
| 15 | `test_mobile_strategy_validation` | Validates mobile wallet payments (`wallet`, `mobile`). | **PASSED** |
| 16 | `test_upi_strategy_validation` | Validates UPI payment processors (`upi`, `gpay`, `phonepe`). | **PASSED** |
| 17 | `test_open_closed_principle_dynamic_extension` | Verifies dynamic registration of a new `GiftCardStrategy` at runtime without altering core code (OCP). | **PASSED** |

---

### Category E: REST API User Story Functional Tests
**File**: `tests/test_api_products.py` | **Scope**: Postman / Newman Functional API

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 18 | `test_api_login` | Validates administrator authentication via JSON payload (`POST /api/auth/login`). | **PASSED** |
| 19 | `test_us01_add_new_product` | US-01 (SCRUM-22): Automated product creation with price formatting (`POST /api/products`). | **PASSED** |
| 20 | `test_us02_view_product_inventory` | US-02 (SCRUM-23): Automated inventory catalog retrieval (`GET /api/products`). | **PASSED** |
| 21 | `test_us03_update_product_details` | US-03 (SCRUM-24): Automated product update & stock adjustment (`PUT /api/products/<id>`). | **PASSED** |
| 22 | `test_us04_delete_product` | US-04 (SCRUM-25): Automated deletion & 404 verification (`DELETE /api/products/<id>`). | **PASSED** |

---

### Category F: Authentication & Role-Based Access Control
**File**: `tests/test_auth.py`

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 23 | `test_login_success` | Validates admin and cashier credentials, establishing user session. | **PASSED** |
| 24 | `test_login_rejects_wrong_password` | Rejects invalid credentials and displays warning flash message. | **PASSED** |

---

### Category G: Products & Catalog Integration
**File**: `tests/test_products.py`

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 25 | `test_admin_can_add_product` | Role check: Admin can add new catalog items with SKU, prices, and opening stock. | **PASSED** |
| 26 | `test_stock_cannot_be_adjusted_below_zero` | Web UI validation: Rejects manual web adjustments that would cause negative inventory. | **PASSED** |
| 27 | `test_stock_adjustment_persists_in_database` | Web UI persistence: Validates stock adjustment updates quantity and commits changes to SQLite. | **PASSED** |

---

### Category H: End-to-End Sales & Receipt Flow
**File**: `tests/test_sales.py`

| # | Test Name | Target Functionality / Business Rule | Outcome |
| :---: | :--- | :--- | :---: |
| 28 | `test_sale_reduces_stock_and_calculates_total` | Full integration test: Checkout form submission, stock decrease, total calculation, receipt display. | **PASSED** |
| 29 | `test_sale_rejects_quantity_above_stock` | Full integration test: Web form rejects sales when requested quantity exceeds inventory. | **PASSED** |

---

## 3. Where to View the Results

1. **Interactive Visual HTML Report**:
   - File Path: [reports/test_report.html](file:///D:/SmartStock/reports/test_report.html)
   - Double-click or open in any web browser to view the interactive test dashboard with filtering, search, and timing metrics.

2. **Standard JUnit XML Report**:
   - File Path: [reports/junit_report.xml](file:///D:/SmartStock/reports/junit_report.xml)
   - Standard format compatible with Jenkins, SonarQube, and CI dashboards.

3. **Live GitHub Actions Run (Online)**:
   - Run URL: [https://github.com/Heetpatel22/SmartStock/actions](https://github.com/Heetpatel22/SmartStock/actions)
   - Shows the live green tick (`✓`) on the GitHub repository.
