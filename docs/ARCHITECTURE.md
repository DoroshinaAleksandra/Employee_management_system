# System Architecture: Employee Management System

This document outlines the internal architecture of the application, the chosen technology stack, and the data flow principles.

---

## 1. Technology Stack & Justification

To achieve maximum efficiency and meet the advanced project requirements, the following stack was selected:

* NiceGUI — web UI framework (Python-native, no HTML/CSS needed)

* SQLAlchemy + SQLite — utilized for ORM and database management. SQLite ensures deployment simplicity (local file storage), while SQLAlchemy provides a robust, object-oriented approach to database interactions.

* Pydantic — implemented for strict data validation at the backend level before any database transactions occur.

* Pytest — testing framework used to ensure the reliability of the business logic and database operations.

---

## 2. Database Schema (SQLAlchemy)

Data persistence is handled via the employees table. The database model (models.py) includes the following fields:

* `id` (Integer, Primary Key) — unique identifier.

* `full_name` (String) — employee's full name.

* `birth_date` (Date, Optional) — date of birth.

* `hire_date` (Date, Optional) — employment start date.

* `position` (String, Optional) — job title.

* `salary` (Float) — employee's salary.

* `currency` (String, Optional) — salary currency (e.g., USD, EUR, RUB).

* `timezone` (String, Optional) — employee's local timezone.

---

## 3. Data Validation (Pydantic)

Input data verification and sanitization are centralized in `schemas.py`. Upon employee creation or update, the payload is validated against the `EmployeeCreate` schema, which enforces:

* Type checking (e.g., ensuring salary is a float).

* Logical constraints (e.g., salary > 0, logical boundary checks for dates). Invalid payloads are rejected before interacting with the database.

---

## 4. Project Structure & Modularity

The application is divided into logical modules to maintain separation of concerns:

* `database.py` — connection setup, engine, and session management.

* `models.py` — SQLAlchemy table definitions.

* `schemas.py` — Pydantic schemas for data validation.

* `services.py` (CRUD) — core business logic functions (Create, Read, Update, Delete) isolated from the UI layer.

* `main.py` — application entry point, NiceGUI initialization, and UI rendering.

* `tests/` — directory containing Pytest unit tests for backend logic.

---

## 5. Project Structure

```
Employee_management_system/
├── README.md # Project description
├── requirements.txt # Dependencies
├── .gitignore # Git ignore rules
├── .github/
│  └── workflows/
│   └── ci.yml # CI/CD pipeline (GitHub Actions)
│
├── src/
│ └── management_system/
│ ├── __init__.py
│ ├── main.py # NiceGUI UI entry point
│ ├── database.py # DB connection, session management
│ ├── models.py # SQLAlchemy table definitions
│ ├── schemas.py # Pydantic validation schemas
│ └── services.py # CRUD operations
│
├── tests/
│ ├── __init__.py
│ ├── test_main.py
│ ├── conftest.py # Pytest fixtures & configuration
│ ├── test_schemas.py # Validation tests
│ └── test_services.py # CRUD logic tests
│
├── docs/
│ ├── API.md
│ ├── ARCHITECTURE.md # This document
│ ├── INSTALL.md
│ └── README.md
│
├── .pylintrc # Pylint configuration
└── pytest.ini # Pytest configuration
```

---

## 6. Data Flow

The user submits data via the web form (NiceGUI).

The payload is routed to the business logic layer (`services.py`).

Data is passed through Pydantic schemas (`schemas.py`) for validation. If validation fails, an exception is raised, and the transaction is aborted.

If valid, SQLAlchemy maps the data to an object and commits the SQL transaction to the SQLite database.

The updated employee record is retrieved from the database and rendered back to the UI table.
