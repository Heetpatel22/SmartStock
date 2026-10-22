# SmartStock Software Requirements Specification

## 1. Problem statement

Small businesses often record stock and sales manually. This can cause incorrect quantities, missing sales records, delayed restocking, and difficulty calculating revenue. SmartStock provides one system for managing products, suppliers, stock movements, sales, and receipts.

## 2. Target users

- Administrator or business owner
- Inventory manager
- Cashier or sales attendant

## 3. Functional requirements

### Authentication

- The system shall allow users to register and log in.
- The system shall assign the first account the administrator role.
- The system shall restrict product, category, supplier, and stock changes to administrators.

### Product and category management

- The administrator shall add, edit, search, and delete eligible products.
- Each product shall store a unique SKU, name, prices, quantity, reorder level, category, and supplier.
- The system shall identify products whose quantity is at or below the reorder level.

### Inventory management

- The administrator shall increase or decrease stock using a reason.
- The system shall prevent stock from becoming negative.
- The system shall record an audit trail for opening stock, manual adjustments, product edits, and sales.

### Supplier management

- The administrator shall add and edit supplier records.
- Supplier records may contain a name, phone number, email address, and physical address.

### Sales and receipts

- An authenticated user shall create a sale by selecting quantities of available products.
- The system shall reject quantities that exceed available stock.
- The system shall calculate subtotals and the transaction total.
- Completing a sale shall reduce inventory automatically.
- The system shall generate a printable receipt and retain the sale in sales history.

### Reporting

- The dashboard shall display product count, units in stock, daily sales, total revenue, recent sales, and low-stock alerts.

## 4. Non-functional requirements

- **Usability:** Core actions should be reachable from a consistent navigation bar.
- **Maintainability:** The system should use modules, blueprints, services, and database models.
- **Security:** Passwords must be hashed and protected routes must require authentication.
- **Reliability:** Stock and sales rules must be validated on the server.
- **Testability:** Business rules and user workflows must be covered by automated tests.
- **Portability:** The application should run on Windows, Linux, or macOS with Python.

## 5. Acceptance criteria

The MVP is accepted when an administrator can register, create categories and suppliers, add products, adjust stock, complete a sale, print a receipt, review sales history, and see the updated dashboard without stock becoming negative.
