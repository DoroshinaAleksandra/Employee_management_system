# System Architecture: Employee Management System

This document outlines the internal architecture of the application, the chosen technology stack, and the data flow principles.

## 1. Project Structure

```
Employee_management_system/
├── README.md # Project description
├── requirements.txt # Dependencies
├── .gitignore # Git ignore rules
├── .github/
│  └── workflows/
│      └── ci.yml # CI/CD pipeline (GitHub Actions)
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

The application is divided into logical modules to maintain separation of concerns:

* `database.py` — handles connection setup, engine creation, and SessionLocal management.
* `models.py` — contains SQLAlchemy table definitions. 
  * `Class Employee`: maps to the `employees` table and defines the data schema (id, full_name, birth_date, hire_date, position, salary, currency, timezone).
* `schemas.py` — contains Pydantic schemas for data validation. 
  * `Class EmployeeCreate`: validates payload before inserting into the database (full_name ≥ 2 words, salary ≥ 0, currency 3 chars).
  * `Class EmployeeRead`: defines the structure of data returned to the UI (includes `id`, uses `from_attributes=True`).
* `services.py` — contains core business logic functions (Create, Read, Update, Delete) isolated from the UI layer.
  * `Class EmployeeService`: CRUD operations with Session management (add, commit, refresh, close).
* `main.py` — application entry point, NiceGUI initialization, and UI rendering.
* `tests/` — directory containing Pytest unit tests for backend logic.

---

## 2. Architecture Diagrams 

### System Components Diagram

```mermaid
graph TD
    UI[NiceGUI Web Interface<br/>main.py] -->|User Input| S[Services Layer<br/>services.py]
    S -->|Validate Payload| P[Pydantic Schemas<br/>schemas.py]
    P -->|Valid Data| S
    S -->|ORM Mapping| M[SQLAlchemy Models<br/>models.py]
    M -->|Read/Write| DB[(SQLite Database<br/>employees.db)]
```

### Data Flow Sequence Diagram

```mermaid 
sequenceDiagram
    actor User
    participant GUI as NiceGUI (main.py)
    participant SVC as EmployeeService (services.py)
    participant PYD as Pydantic (schemas.py)
    participant DB as SessionLocal (database.py)
    participant ORM as Employee (models.py)
    participant SQL as SQLite (employees.db)

    User->>GUI: Fill form & click "Add"
    GUI->>SVC: service.create(employee_data)
    
    Note over SVC,PYD: Validation Phase
    SVC->>PYD: EmployeeCreate(**employee_data)
    
    alt Validation Fails
        PYD-->>SVC: Raises ValidationError
        SVC-->>GUI: Returns error (None)
        GUI-->>User: Shows error message
    else Validation Passes
        PYD-->>SVC: Returns validated EmployeeCreate object
        
        Note over SVC,SQL: Database Operation Phase
        SVC->>DB: SessionLocal() (get session)
        DB-->>SVC: Returns db session
        
        SVC->>ORM: Employee(**validated_data.model_dump())
        ORM-->>SVC: Returns Employee instance (not saved yet)
        
        SVC->>DB: db.add(employee)
        SVC->>DB: db.commit()
        DB->>SQL: INSERT INTO employees ...
        SQL-->>DB: Returns new record with ID
        
        SVC->>DB: db.refresh(employee)
        DB-->>SVC: Updated employee with ID
        
        SVC->>DB: db.close()
        DB-->>SVC: Session closed
        
        SVC-->>GUI: Returns employee object
        GUI-->>User: Displays updated table
    end
```

---

## 3. Components Interaction & Data Flow

1. The user submits data via the web form (NiceGUI).

2. The payload is routed to the business logic layer (`services.py`).

3. Data is passed through Pydantic schemas (`schemas.py`) for validation. If validation fails, an exception is raised, and the transaction is aborted.

4. If valid, SQLAlchemy maps the data to an object and commits the SQL transaction to the SQLite database.

5. The updated employee record is retrieved from the database and rendered back to the UI table.
