"""
Generates a publication-quality diagram of the Agile Testing Quadrants (Brian Marick framework)
specifically customized with all SmartStock project test implementations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup figure with high resolution
fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Background styling
fig.patch.set_facecolor("#0F172A")  # Slate 900
ax.set_facecolor("#0F172A")

# Title and Subtitle
ax.text(
    50, 96.5,
    "AGILE TESTING QUADRANTS (BRIAN MARICK FRAMEWORK)",
    fontsize=18, fontweight="bold", color="#F8FAFC", ha="center", va="center",
    fontfamily="sans-serif"
)
ax.text(
    50, 93.5,
    "SmartStock Inventory & Sales Management System — CSE706 Testing Deliverable",
    fontsize=11, color="#94A3B8", ha="center", va="center",
    fontfamily="sans-serif"
)

# Axis definitions
# Vertical line: Business Facing (Top) <-> Technology Facing (Bottom)
ax.annotate(
    "", xy=(50, 91), xytext=(50, 9),
    arrowprops=dict(arrowstyle="<->", color="#64748B", lw=2, mutation_scale=15)
)
# Horizontal line: Supporting the Team (Left) <-> Critiquing the Product (Right)
ax.annotate(
    "", xy=(97, 50), xytext=(3, 50),
    arrowprops=dict(arrowstyle="<->", color="#64748B", lw=2, mutation_scale=15)
)

# Axis Labels
# Top: Business Facing
ax.text(50, 91.5, "▲ BUSINESS FACING", fontsize=11, fontweight="bold", color="#38BDF8", ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1E293B", edgecolor="#38BDF8", lw=1))
# Bottom: Technology Facing
ax.text(50, 8.5, "▼ TECHNOLOGY FACING", fontsize=11, fontweight="bold", color="#38BDF8", ha="center", va="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1E293B", edgecolor="#38BDF8", lw=1))
# Left: Supporting the Team
ax.text(2.5, 50, "◄ SUPPORTING THE TEAM", fontsize=10, fontweight="bold", color="#38BDF8", ha="left", va="center", rotation=90,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1E293B", edgecolor="#38BDF8", lw=1))
# Right: Critiquing the Product
ax.text(97.5, 50, "CRITIQUING THE PRODUCT ►", fontsize=10, fontweight="bold", color="#38BDF8", ha="right", va="center", rotation=-90,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1E293B", edgecolor="#38BDF8", lw=1))

# Helper to draw quadrant cards
def draw_quadrant(x, y, w, h, bg_color, border_color, badge_text, badge_color, title, subtitle, items):
    # Main Card
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=1.5,rounding_size=2.0",
        facecolor=bg_color, edgecolor=border_color, lw=1.8,
        alpha=0.95
    )
    ax.add_patch(rect)
    
    # Badge (e.g. Q2: Automated Functional)
    ax.text(
        x + 2, y + h - 3,
        badge_text,
        fontsize=10, fontweight="bold", color="#FFFFFF",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=badge_color, edgecolor="none")
    )
    
    # Title & Subtitle
    ax.text(x + 2, y + h - 7, title, fontsize=12, fontweight="bold", color="#F8FAFC", va="top")
    ax.text(x + 2, y + h - 10.5, subtitle, fontsize=9.5, fontstyle="italic", color="#CBD5E1", va="top")
    
    # Bullet points
    current_y = y + h - 15
    for item in items:
        ax.text(x + 2.5, current_y, f"•  {item}", fontsize=9, color="#E2E8F0", va="top", fontfamily="sans-serif")
        current_y -= 4.2

# -------------------------------------------------------------
# Q2: Top-Left (Business Facing + Supporting Team)
# -------------------------------------------------------------
draw_quadrant(
    x=5.5, y=52.5, w=41.5, h=36,
    bg_color="#1E293B", border_color="#3B82F6",  # Blue
    badge_text="QUADRANT 2: FUNCTIONAL", badge_color="#2563EB",
    title="Automated Functional & API Tests",
    subtitle="Tools: Postman Collection, Newman, REST Endpoints",
    items=[
        "US-01 (SCRUM-22): Add Product API validation (201 Created)",
        "US-02 (SCRUM-23): View Inventory with INR (₹) price formatting",
        "US-03 (SCRUM-24): Product Details & stock quantity updates",
        "US-04 (SCRUM-25): Product Deletion & sales safeguard checks",
        "Given-When-Then automated JavaScript test assertions"
    ]
)

# -------------------------------------------------------------
# Q3: Top-Right (Business Facing + Critiquing Product)
# -------------------------------------------------------------
draw_quadrant(
    x=53, y=52.5, w=41.5, h=36,
    bg_color="#1E293B", border_color="#A855F7",  # Purple
    badge_text="QUADRANT 3: EXPLORATORY & UAT", badge_color="#7C3AED",
    title="User Acceptance & Usability Testing",
    subtitle="Tools: Manual Browser Walkthroughs, UI Inspection",
    items=[
        "End-to-End Cashier sales checkout & cart workflow",
        "Printable thermal receipt preview & layout check",
        "Real-time JavaScript subtotal calculation (en-IN locale)",
        "Responsive Bootstrap 5 mobile & desktop experience",
        "Sprint 1 & 2 Pair Programming verification walkthroughs"
    ]
)

# -------------------------------------------------------------
# Q1: Bottom-Left (Technology Facing + Supporting Team)
# -------------------------------------------------------------
draw_quadrant(
    x=5.5, y=11.5, w=41.5, h=36,
    bg_color="#1E293B", border_color="#10B981",  # Emerald Green
    badge_text="QUADRANT 1: UNIT & COMPONENT", badge_color="#059669",
    title="Automated Unit / TDD Architecture",
    subtitle="Tools: Pytest, xUnit, GitHub Actions CI, Git Hooks",
    items=[
        "24 Automated Test Cases executed (100% Pass rate)",
        "Module 1 TDD: InventoryService stock boundary tests",
        "Module 2 TDD: SalesService checkout & receipt generation",
        "SOLID Principles: Interface segregation & Strategy pattern",
        "Continuous Integration: Pre-commit hook & GitHub Actions"
    ]
)

# -------------------------------------------------------------
# Q4: Bottom-Right (Technology Facing + Critiquing Product)
# -------------------------------------------------------------
draw_quadrant(
    x=53, y=11.5, w=41.5, h=36,
    bg_color="#1E293B", border_color="#F59E0B",  # Amber/Orange
    badge_text="QUADRANT 4: NON-FUNCTIONAL", badge_color="#D97706",
    title="Security, Performance & Operational",
    subtitle="Tools: Security Audits, Database ACID Integrity",
    items=[
        "Role-Based Access Control (@admin_required decorator)",
        "Secure Password Hashing using PBKDF2:SHA256 (Werkzeug)",
        "ACID Database Transactions & Rollback on failure",
        "Input sanitization & boundary defense (prevent negative stock)",
        "High-performance sub-second API endpoint latency"
    ]
)

# Save to destination
output_path = r"D:\SmartStock\docs\agile_testing_quadrants.png"
plt.tight_layout()
plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
plt.close()

print(f"Diagram successfully generated at: {output_path}")

