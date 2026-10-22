# SmartStock Project Plan

## Proposed team roles

| Role | Responsibilities |
|---|---|
| Project manager / requirements lead | Backlog, meetings, requirements, presentation coordination |
| Backend developer | Models, authentication, services, validation |
| Frontend developer | Templates, Bootstrap interface, accessibility and usability |
| QA and DevOps engineer | Pytest, GitHub Actions, pull-request checks, deployment |

Team members can rotate code-review and testing responsibilities.

## Suggested Git workflow

1. Keep stable code on `main`.
2. Integrate completed features on `development`.
3. Create feature branches such as `feature/product-management`.
4. Open pull requests into `development`.
5. Require a passing GitHub Actions test and at least one review.
6. Merge `development` into `main` for demonstration releases.

## Initial backlog

| ID | User story | Priority | Status in MVP |
|---|---|---:|---|
| SS-01 | As a user, I can register and log in securely. | High | Complete |
| SS-02 | As an administrator, I can manage products. | High | Complete |
| SS-03 | As an administrator, I can organize products by category. | Medium | Complete |
| SS-04 | As an administrator, I can manage suppliers. | Medium | Complete |
| SS-05 | As an administrator, I can adjust stock with a reason. | High | Complete |
| SS-06 | As a cashier, I can complete a sale. | High | Complete |
| SS-07 | As a cashier, I receive a printable receipt. | High | Complete |
| SS-08 | As an owner, I can see low-stock alerts and revenue totals. | High | Complete |
| SS-09 | As an owner, I can export reports to Excel or PDF. | Medium | Planned |
| SS-10 | As a cashier, I can scan product barcodes. | Low | Planned |

## SOLID and design evidence

- **Single Responsibility:** Authentication routes, inventory rules, sales rules, models, and UI templates are separated.
- **Open/Closed:** Additional payment methods, report types, and stock movement reasons can be added without replacing the core sales workflow.
- **Liskov Substitution:** User authorization relies on shared user behavior and role properties rather than route-specific user types.
- **Interface Segregation:** Cashiers see selling and reporting features while administrative changes are protected.
- **Dependency Inversion:** Routes delegate stock and sales rules to service classes instead of embedding all business logic in views.

## Testing evidence

The included tests cover:

- Successful and unsuccessful login
- Adding a product
- Preventing negative inventory
- Completing a sale
- Correct total calculation
- Automatic stock reduction
- Preventing sales above available stock

## Demonstration sequence

1. Register or log in as administrator.
2. Add a category and supplier.
3. Add a product and show its reorder level.
4. Adjust stock and show movement history.
5. Create a sale with multiple products.
6. Show the generated receipt.
7. Return to the dashboard and show changed stock and revenue.
8. Show tests and the GitHub Actions workflow.
9. Show the GitHub project board, issues, branches, commits, and pull requests.
