"""
Tests for CRUD operations on EmployeeService.
"""
from src.management_system.schemas import EmployeeCreate


class TestCreateEmployee:
    """
    Tests for creating employees.
    """

    def test_create_employee_success(self, service, employee_data):
        """
        Test: successful employee creation.
        """
        created = service.create(employee_data)

        assert created.id is not None
        assert created.full_name == "Иванов Иван Иванович"
        assert created.salary == 150000.0
        assert created.position == "Backend Developer"

    def test_create_employee_with_zero_salary(self, service):
        """
        Test: creating employee with zero salary (valid).
        """
        emp_data = EmployeeCreate(
            full_name="Петров Петр",
            salary=0
        )
        created = service.create(emp_data)

        assert created.salary == 0

    def test_create_multiple_employees(self, service, employee_data):
        """
        Test: creating multiple employees.
        """
        service.create(employee_data)
        service.create(EmployeeCreate(full_name="Петрова Анна", salary=120000))

        all_emps = service.get_all()
        assert len(all_emps) == 2


class TestReadEmployees:
    """
    Tests for reading employees.
    """

    def test_get_all_empty(self, service):
        """
        Test: get all employees from empty database.
        """
        all_emps = service.get_all()
        assert len(all_emps) == 0

    def test_get_all_with_data(self, service, employee_data):
        """
        Test: get all employees (with data).
        """
        service.create(employee_data)
        service.create(EmployeeCreate(full_name="Петрова Анна", salary=120000))

        all_emps = service.get_all()
        assert len(all_emps) == 2

    def test_get_by_id_exists(self, service, created_employee):
        """
        Test: get employee by ID (exists).
        """
        found = service.get_by_id(created_employee.id)

        assert found is not None
        assert found.full_name == "Иванов Иван Иванович"

    def test_get_by_id_not_exists(self, service):
        """
        Test: get employee by ID (does not exist).
        """
        found = service.get_by_id(999)
        assert found is None


class TestUpdateEmployee:
    """
    Tests for updating employees.
    """

    def test_update_salary(self, service, created_employee):
        """
        Test: salary update.
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
        Test: update multiple fields simultaneously.
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
        Test: update only position (other fields remain unchanged).
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
        Test: update non-existent employee.
        """
        updated = service.update(999, employee_data)
        assert updated is None


class TestDeleteEmployee:
    """
    Tests for deleting employees.
    """

    def test_delete_success(self, service, created_employee):
        """
        Test: successful deletion.
        """
        deleted = service.delete(created_employee.id)

        assert deleted is True
        assert service.get_by_id(created_employee.id) is None

    def test_delete_not_exists(self, service):
        """
        Test: delete non-existent employee.
        """
        deleted = service.delete(999)
        assert deleted is False
