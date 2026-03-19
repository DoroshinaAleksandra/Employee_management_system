"""
Тесты на CRUD-операции EmployeeService.
"""
from src.management_system.schemas import EmployeeCreate


class TestCreateEmployee:
    """
    Тесты на создание сотрудников.
    """

    def test_create_employee_success(self, service, employee_data):
        """
        Тест: успешное создание сотрудника.
        """
        created = service.create(employee_data)

        assert created.id is not None
        assert created.full_name == "Иванов Иван Иванович"
        assert created.salary == 150000.0
        assert created.position == "Backend Developer"

    def test_create_employee_with_zero_salary(self, service):
        """
        Тест: создание сотрудника с нулевой зарплатой (валидно).
        """
        emp_data = EmployeeCreate(
            full_name="Петров Петр",
            salary=0
        )
        created = service.create(emp_data)

        assert created.salary == 0

    def test_create_multiple_employees(self, service, employee_data):
        """
        Тест: создание нескольких сотрудников.
        """
        service.create(employee_data)
        service.create(EmployeeCreate(full_name="Петрова Анна", salary=120000))

        all_emps = service.get_all()
        assert len(all_emps) == 2


class TestReadEmployees:
    """
    Тесты на чтение сотрудников.
    """

    def test_get_all_empty(self, service):
        """
        Тест: получение данных всех сотрудников из пустой базы.
        """
        all_emps = service.get_all()
        assert len(all_emps) == 0

    def test_get_all_with_data(self, service, employee_data):
        """
        Тест: получение данных всех сотрудников (есть данные).
        """
        service.create(employee_data)
        service.create(EmployeeCreate(full_name="Петрова Анна", salary=120000))

        all_emps = service.get_all()
        assert len(all_emps) == 2

    def test_get_by_id_exists(self, service, created_employee):
        """
        Тест: получение сотрудника по ID (существует).
        """
        found = service.get_by_id(created_employee.id)

        assert found is not None
        assert found.full_name == "Иванов Иван Иванович"

    def test_get_by_id_not_exists(self, service):
        """
        Тест: получение сотрудника по ID (не существует).
        """
        found = service.get_by_id(999)
        assert found is None


class TestUpdateEmployee:
    """
    Тесты на обновление данных сотрудников.
    """

    def test_update_salary(self, service, created_employee):
        """
        Тест: обновление зарплаты.
        """
        updated = service.update(
            created_employee.id,
            EmployeeCreate(
                full_name=created_employee.full_name,
                salary=200000
            )
        )

        assert updated.salary == 200000

    def test_update_multiple_fields(self, service, created_employee):
        """
        Тест: обновление нескольких полей одновременно.
        """
        updated = service.update(
            created_employee.id,
            EmployeeCreate(
                full_name="Петров Петр Петрович",
                salary=300000,
                position="CTO"
            )
        )

        assert updated.full_name == "Петров Петр Петрович"
        assert updated.salary == 300000
        assert updated.position == "CTO"

    def test_update_partial_fields(self, service, created_employee):
        """
        Тест: обновление только должности (остальные поля не меняются).
        """
        original_name = created_employee.full_name
        original_salary = created_employee.salary

        updated = service.update(
            created_employee.id,
            EmployeeCreate(
                full_name=original_name,
                salary=original_salary,
                position="Senior Developer"
            )
        )

        assert updated.position == "Senior Developer"
        assert updated.full_name == original_name
        assert updated.salary == original_salary

    def test_update_not_exists(self, service, employee_data):
        """
        Тест: обновление несуществующего сотрудника.
        """
        updated = service.update(999, employee_data)
        assert updated is None


class TestDeleteEmployee:
    """
    Тесты на удаление сотрудников.
    """

    def test_delete_success(self, service, created_employee):
        """
        Тест: успешное удаление.
        """
        deleted = service.delete(created_employee.id)

        assert deleted is True
        assert service.get_by_id(created_employee.id) is None

    def test_delete_not_exists(self, service):
        """
        Тест: удаление несуществующего сотрудника.
        """
        deleted = service.delete(999)
        assert deleted is False
