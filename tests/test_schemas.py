"""
Tests for Pydantic schema validation.
"""
import pytest
from pydantic import ValidationError
from src.management_system.schemas import EmployeeCreate


class TestEmployeeCreateValid:
    """
    Tests for valid data.
    """

    def test_valid_minimal_data(self):
        """
        Test: minimal valid data (only required fields).
        """
        emp = EmployeeCreate(full_name="Иван Иванов", salary=50000)

        assert emp.full_name == "Иван Иванов"
        assert emp.salary == 50000
        assert emp.currency == "RUB"  # default
        assert emp.timezone == "UTC+3"  # default

    def test_valid_full_data(self):
        """
        Test: all fields provided.
        """
        emp = EmployeeCreate(
            full_name="Петрова Анна Сергеевна",
            salary=120000,
            currency="USD",
            timezone="UTC-5"
        )

        assert emp.currency == "USD"
        assert emp.timezone == "UTC-5"


class TestEmployeeCreateInvalid:
    """
    Tests for invalid data.
    """

    def test_invalid_salary_negative(self):
        """
        Test: negative salary is rejected.
        """
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name="Иван Иванов", salary=-100)

    def test_invalid_salary_zero_allowed(self):
        """
        Test: zero salary is allowed (ge=0).
        """
        emp = EmployeeCreate(full_name="Иван Иванов", salary=0)
        assert emp.salary == 0

    def test_invalid_name_one_word(self):
        """
        Test: single-word full name is rejected.
        """
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name="Иван", salary=50000)

    def test_invalid_name_two_words_allowed(self):
        """
        Test: two-word full name is allowed.
        """
        emp = EmployeeCreate(full_name="Иван Иванов", salary=50000)
        assert emp.full_name == "Иван Иванов"

    def test_invalid_name_three_words(self):
        """
        Test: three-word full name is allowed.
        """
        emp = EmployeeCreate(full_name="Иванов Иван Иванович", salary=50000)
        assert emp.full_name == "Иванов Иван Иванович"

    def test_invalid_currency_length(self):
        """
        Test: currency code with invalid length is rejected.
        """
        with pytest.raises(ValidationError):
            EmployeeCreate(
                full_name="Иван Иванов",
                salary=50000,
                currency="RUBL"
            )


@pytest.mark.parametrize(
    "full_name,salary,should_pass",
    [
        ("Иван Иванов", 50000, True),
        ("Петрова Анна", 75000, True),
        ("Иванов Иван Иванович", 100000, True),
        ("Иван", 50000, False),
        ("Иван Иванов", -100, False),
        ("Иван Иванов", 0, True),
    ],
)
def test_employee_create_parametrized(full_name, salary, should_pass):
    """
    Parametrized test: various data combinations.
    """
    if should_pass:
        emp = EmployeeCreate(full_name=full_name, salary=salary)
        assert emp.full_name == full_name
        assert emp.salary == salary
    else:
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name=full_name, salary=salary)
