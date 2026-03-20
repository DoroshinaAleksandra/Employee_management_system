"""
Фикстуры для тестов системы управления сотрудниками.
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
    Создаём тестовую базу данных в памяти (SQLite :memory:).
    База создаётся заново для каждого теста и удаляется после.
    """
    # Создаём движок БД в памяти (не на диске!)
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Создаём все таблицы (employees)
    Base.metadata.create_all(bind=engine)

    # Создаём сессию для работы с БД
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    # Отдаём сессию тесту
    yield session

    # После теста закрываем сессию и удаляем БД
    session.close()
    engine.dispose()


@pytest.fixture
def service(db_session):
    """
    Создаёт EmployeeService для тестов.
    Использует фикстуру db_session.
    """
    return EmployeeService(db_session)


@pytest.fixture
def employee_data():
    """
    Тестовые данные для создания сотрудника.
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
    Создаёт реального сотрудника в тестовой БД.
    Использует service и employee_data.
    """
    return service.create(employee_data)
