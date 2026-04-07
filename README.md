# Zorvyn Financial Management Backend

A comprehensive, robust, and cleanly-layered backend API for tracking financial records, performing data analytics, and enforcing Role-Based Access Control (RBAC).

##  Key Features

*   **FastAPI & Pydantic**: Leverages FastAPI for high-performance routing and OpenAPI documentation generation, with Pydantic enforcing strict type safety and request validation.
*   **Clean Layered Architecture**: Decoupled design prioritizing maintainability. Routes handle HTTP, Services handle core business logic, and Repositories handle SQLAlchemy database queries.
*   **Secure Authentication**: Implements JWT (JSON Web Token) Bearer authentication for state-less, secure access.
*   **Role-Based Access Control (RBAC)**: Deeply integrated permission structures.
    *   **Admin**: Full global access, including User Management (can create/delete any users) and global financial record tracking.
    *   **Analyst**: Read-only global visibility to monitor overall financial trends and calculate global growth metrics.
    *   **Viewer**: Strictly isolated to their own financial records and dashboard analytics.
*   **Advanced Analytics Engine**: On-the-fly dashboard aggregations calculating Net Balance, Savings Rates, and Month-over-Month (MoM) Growth Percentages directly translated into chronological JSON payloads.
*   **100% Test Coverage Stability**: A comprehensive Pytest suite powered by an isolated, in-memory `StaticPool` SQLite environment decoupled from the production disk database.

---

##  Architectural Layers

The system adheres to a strict separation of concerns to avoid logic bleeding:

1.  **API Layer** (`app/api/`): Defines the FastAPI routers. Responsibilities: Accepting HTTP requests, parsing query parameters (e.g., specific `datetime.date` mappings to power Swagger UI Date Pickers), ensuring the presence of the `Depends()` security contexts, and returning the structured Pydantic models.
2.  **Service Layer** (`app/services/`): The core business engine. Responsibilities: Orchestrating data manipulation, applying mathematical analytics (like calculating division-by-zero safe savings rates), and enforcing complex object-level permissions.
3.  **Repository Layer** (`app/repositories/`): Pure database interaction. Responsibilities: Fetching, filtering, and inserting data into the SQLAlchemy models. Converts Python filtering instructions into raw SQLite queries.
4.  **Database/Models** (`app/db/`): Manages the relational mappings. Replaced complex relational `Category` models with high-performance `Literal` String Enums for maximum reliability.

---

##  Security & Access Flow

When a request arrives, such as creating a new User via `POST /api/v1/users/`:
1.  **Token Interception**: The `reusable_oauth2` dependency extracts the Bearer token.
2.  **Signature Verification**: The `jose` JWT utility decodes the token. If corrupted, missing, or expired, a `401 Unauthorized` is bounced back.
3.  **Database Validation**: The user's ID is cross-referenced with the active SQLite database to ensure the user still exists.
4.  **Role Enforcement**: The `get_current_active_superuser` dependency verifies the `is_superuser` flag. If a Viewer or Analyst attempts the request, a `403 Forbidden` acts as an absolute firewall.
5.  **Execution**: Only after clearing all checks is the service function invoked.

---

##  Dashboard Analytics Endpoints

The system exposes highly dynamic dashboard endpoints (`/api/v1/dashboard/*`):
*   **/summary**: Aggregates total income and expenses within specific `start_date` and `end_date` bounds.
*   **/trends**: Groups records chronologically using SQLite `strftime`, bounded dynamically by a `months` limit, calculating Net Profit, Savings Rate %, and Month-over-Month Growth (Income/Expense). 
*   **/category-breakdown**: Determines the percentage allocation of capital across system-wide accepted Enums (Housing, Food, Transportation, Salary, Misc).

---

##  Quick Setup & Installation

### 1. Initialize Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed the Database
Before running the server, initialize the SQLite file and inject the required core roles and testing accounts.
```bash
python seed_db.py
```
*This script provisions three testing accounts (admin@zorvyn.com, analyst@zorvyn.com, viewer@zorvyn.com) all sharing the exact same password: `password123`. The admin account includes pre-populated financial data.*

### 3. Launch the Application
```bash
uvicorn app.main:app --reload
```
Navigate your browser to `http://127.0.0.1:8000/docs` to interface with the fully interactive Swagger UI documentation. Click the **Authorize** lock to log in.

### 4. Execute the Test Suite
```bash
pytest -v
```
Runs the entire local test suite against a temporary in-memory `StaticPool` database, guaranteeing zero collisions with your active `sql_app.db` records.
