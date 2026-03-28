# Code Reference

This document provides detailed information about the internal structure, classes, functions, and testing infrastructure of the Employee Management System. 

For general project overview, installation instructions, and usage guides, please refer to the [README](../README.md).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Reference](#module-reference)
   - [main.py (UI Layer)](#mainpy-ui-layer)
   - [services.py (Business Logic)](#servicespy-business-logic)
   - [schemas.py (Validation)](#schemaspy-validation)
   - [models.py (Database Models)](#modelspy-database-models)
   - [database.py (Connection)](#databasepy-connection)
   - [constants.py (Configuration)](#constantspy-configuration)
3. [Testing Infrastructure](#testing-infrastructure)

---

## Architecture Overview

The application follows a layered architecture to ensure separation of concerns, testability, and maintainability.

User -> EmployeeApp -> [DatabaseManager | EmployeeTableView | EmployeeDialogManager]
                              |
                              v
                    EmployeeDialogManager -> Pydantic -> EmployeeService -> SQLAlchemy -> SQLite
                              |
                              v
                    EmployeeTableView <- (callback: on_data_changed) <- refresh UI

Detailed architecture diagrams and data flow sequences can be found in [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Module Reference

### main.py (UI Layer)

The entry point of the application. Handles the NiceGUI interface initialization and user interaction events.

#### Class: `DatabaseManager`
Manages database connections and session lifecycle.

| Method / Attribute | Description |
| :--- | :--- |
| `__init__()` | Initializes `db_session` and `service` as `None`. |
| `initialize_db()` | Calls `init_db()` and then `refresh_session()`. |
| `refresh_session()` | Closes existing session (if any), creates new `SessionLocal`, and initializes `EmployeeService`. |
| `get_service()` | Returns the `EmployeeService` instance for CRUD operations. |

#### Class: `EmployeeTableView`
Renders the employee table with CRUD action buttons.

| Method / Attribute | Description |
| :--- | :--- |
| `__init__(container, db_manager, on_edit_callback, on_delete_callback)` | Initializes with UI container, database manager, and callback functions. |
| `render()` | Fetches employees via `db_manager`, clears container, renders table rows or empty state message. |

#### Class: `EmployeeDialogManager`
Handles all dialog windows (Create, Edit, Delete).

| Method / Attribute | Description |
| :--- | :--- |
| `__init__(db_manager, on_data_changed)` | Initializes with database manager and refresh callback. |
| `open_create_dialog()` | Opens dialog with form inputs for new employee; validates via Pydantic; calls `on_data_changed` on success. |
| `open_edit_dialog(emp_id)` | Opens pre-filled dialog for editing; handles "not found" case with warning notification. |
| `confirm_delete(emp_id)` | Opens confirmation dialog; calls delete service method only after user confirmation. |

#### Class: `EmployeeApp`
Orchestrates all components and builds the main UI.

| Method / Attribute | Description |
| :--- | :--- |
| `__init__()` | Creates `DatabaseManager`; sets `table_view`, `dialog_manager`, `table_container` to `None`. |
| `run()` | Initializes DB via `db_manager`, builds UI, starts NiceGUI server (127.0.0.1:8080). |
| `_build_ui()` | Constructs layout: header, title, "Add Employee" button; instantiates `EmployeeTableView` and `EmployeeDialogManager` with callbacks. |
| `_render_table()` | Delegates to `table_view.render()` if initialized. |
| `_open_create_dialog()` / `_open_edit_dialog()` / `_confirm_delete()` | Delegate to `dialog_manager` methods. |

#### Exceptions

| Exception | Description |
| :--- | :--- |
| `pydantic.ValidationError` | Raised when input data fails schema validation. Caught in `EmployeeDialogManager.save_new()` and `save_changes()` to show user-friendly `ui.notify()` messages. |

---

### services.py (Business Logic)

Contains the core business logic, isolated from the UI layer. Handles database transactions and CRUD operations.

#### Class: `EmployeeService`

| Method | Description |
| :--- | :--- |
| `__init__(db: Session)` | Initializes the service with a SQLAlchemy session. |
| `create(employee: EmployeeCreate)` | Creates a new employee instance, adds it to the session, commits, and refreshes the object. Returns the created model. |
| `get_all()` | Queries the database and returns a list of all employee records. |
| `get_by_id(employee_id: int)` | Filters the database by unique ID. Returns the employee object or `None` if not found. |
| `update(employee_id: int, employee: EmployeeCreate)` | Retrieves the employee by ID. If found, updates attributes based on the input schema, commits, and refreshes. Returns the updated object or `None`. |
| `delete(employee_id: int)` | Retrieves the employee by ID. If found, deletes the record and commits. Returns `True` if successful, `False` if not found. |

> **Note on `update()` Method**
>
> The method requires passing **all mandatory fields** of the `EmployeeCreate` schema (`full_name`, `salary`), even if they remain unchanged.
>
> **Reason:** Pydantic validation occurs prior to the service call. If a mandatory field is omitted, the schema validation will fail.
>
> **Behavior:**
> - Passed fields are updated via `setattr()`.
> - Fields not included in the request **retain their existing values** (provided mandatory fields are passed with their current values).
> - Returns `None` if the employee with the specified `employee_id` is not found.
>
> **Example of Correct Usage:**
> ```python
> # To update only the position, you must also pass the unchanged mandatory fields:
> service.update(
>     employee_id=1,
>     employee=EmployeeCreate(
>         full_name="Ivanov Ivan",  # current name
>         salary=100000,            # current salary
>         position="Senior Developer"  # new value
>     )
> )
> ```

---

### schemas.py (Validation)

Defines Pydantic models for data validation and serialization.

#### Class: `EmployeeCreate`

Schema for input data during creation or updates.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `full_name` | str | `min_length=3`, `max_length=100` | Must contain at least 2 words (validated by `check_name_has_parts`). |
| `birth_date` | date | Optional | Date of birth. |
| `hire_date` | date | Optional | Date of hire. |
| `position` | str | Optional | Job position. |
| `salary` | float | `ge=0` | Salary amount (cannot be negative). |
| `currency` | str | `min_length=3`, `max_length=3` | Currency code (default: "RUB"). |
| `timezone` | str | `max_length=10` | Timezone offset (default: "UTC+3"). |

**Validators:**
- `check_name_has_parts`: Ensures `full_name` contains at least two words (first and last name). Raises `ValueError` if validation fails.

#### Class: `EmployeeRead`

Schema for output data. Configured with `from_attributes=True` to allow instantiation from SQLAlchemy ORM models. Includes all fields from `EmployeeCreate` plus the `id`.

---

### models.py (Database Models)

Defines SQLAlchemy ORM models mapped to the SQLite database.

#### Class: `Employee`

Maps to the `employees` table.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | `primary_key=True`, `index=True` | Unique identifier. |
| `full_name` | String(100) | `nullable=False` | Full name of the employee. |
| `birth_date` | Date | `nullable=True` | Date of birth. |
| `hire_date` | Date | `nullable=True` | Date of hire. |
| `position` | String(50) | `nullable=True` | Job title. |
| `salary` | Float | `nullable=False` | Salary amount. |
| `currency` | String(3) | `default="RUB"` | Currency code. |
| `timezone` | String(10) | `default="UTC+3"` | Timezone offset. |

---

### database.py (Connection)

Handles database engine creation, session management, and table initialization.

| Object / Function | Description |
| :--- | :--- |
| `SQLALCHEMY_DATABASE_URL` | Connection string for SQLite (`sqlite:///./employees.db`). |
| `engine` | SQLAlchemy engine instance created with `check_same_thread=False`. |
| `SessionLocal` | Session factory configured with `autocommit=False` and `autoflush=False`. |
| `Base` | Declarative base class for ORM models. |
| `init_db()` | Creates all tables defined in `models.py` if they do not exist. |
| `get_db()` | Generator function for dependency injection. Yields a session and ensures closure after use. |

---

### constants.py (Configuration)

Stores application-wide constants.

- `CURRENCIES`: List of supported currency codes (RUB, USD, EUR, GBP, CNY, JPY, KZT, BYN).
- `TIMEZONES`: List of supported timezones (UTC-12 to UTC+12).
- `DEFAULT_CURRENCY`: Default currency setting (RUB).
- `DEFAULT_TIMEZONE`: Default timezone setting (UTC+3).

---

## Testing Infrastructure

Tests are located in the `tests/` directory and utilize `pytest`. The testing strategy focuses on unit testing the service layer and schema validation.

### Fixtures (`conftest.py`)

To ensure test isolation, an in-memory SQLite database is used for each test session.

| Fixture | Description |
| :--- | :--- |
| `db_session` | Creates an engine (`sqlite:///:memory:`), creates all tables, yields a session, and disposes of the engine after the test. |
| `service` | Initializes an `EmployeeService` instance using the `db_session` fixture. |
| `employee_data` | Provides a valid `EmployeeCreate` schema object with dummy data for testing. |
| `created_employee` | Uses the `service` and `employee_data` fixtures to create a persisted employee record in the test database. |

### Test Modules

- `test_services.py`: Validates CRUD operations (create, read, update, delete) within the service layer.
- `test_schemas.py`: Validates data constraints (e.g., salary limits, name format) using Pydantic schemas.
- `test_gui.py`: Contains unit tests for all 4 GUI components (EmployeeApp, DatabaseManager, EmployeeTableView, EmployeeDialogManager) using mocks for NiceGUI and database layers.

### Running Tests

To run the test suite, execute the following command in the project root:

```bash
pytest tests -v