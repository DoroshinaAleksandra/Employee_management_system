"""
Fixtures for employee management system tests.
"""
# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.management_system.database import Base
from src.management_system.services import EmployeeService
from src.management_system.schemas import EmployeeCreate


@pytest.fixture
def db_session():
    """
    Creates an in-memory test database (SQLite :memory:).
    Database is recreated for each test and cleaned up afterwards.
    """
    # Create in-memory database engine
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables (employees)
    Base.metadata.create_all(bind=engine)

    # Create session factory for database operations
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    # Yield session to the test
    yield session

    # After test: close session and dispose engine
    session.close()
    engine.dispose()


@pytest.fixture
def service(db_session):
    """
    Creates EmployeeService for tests.
    Uses the db_session fixture.
    """
    return EmployeeService(db_session)


@pytest.fixture
def employee_data():
    """
    Test data for creating an employee.
    """
    return EmployeeCreate(
        full_name="Иванов Иван Иванович",
        birth_date=None,
        hire_date=None,
        position="Backend Developer",
        salary=150000.0,
        currency="RUB",
        timezone="UTC+3"
    )


@pytest.fixture
def created_employee(service, employee_data):
    """
    Creates a real employee in the test database.
    Uses service and employee_data fixtures.
    """
    return service.create(employee_data)
