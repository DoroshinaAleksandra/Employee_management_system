"""
Тесты на валидацию Pydantic-схем.
"""
import pytest
from pydantic import ValidationError
from src.management_system.schemas import EmployeeCreate


class TestEmployeeCreateValid:
    """
    Тесты на корректные данные.
    """

    def test_valid_minimal_data(self):
        """
        Тест: минимальные валидные данные (только обязательные поля).
        """
        emp = EmployeeCreate(full_name="Иван Иванов", salary=50000)

        assert emp.full_name == "Иван Иванов"
        assert emp.salary == 50000
        assert emp.currency == "RUB"  # default
        assert emp.timezone == "UTC+3"  # default

    def test_valid_full_data(self):
        """
        Тест: все поля заполнены.
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
    Тесты на некорректные данные.
    """

    def test_invalid_salary_negative(self):
        """
        Тест: отрицательная зарплата отклоняется.
        """
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name="Иван Иванов", salary=-100)

    def test_invalid_salary_zero_allowed(self):
        """
        Тест: нулевая зарплата проходит (ge=0).
        """
        emp = EmployeeCreate(full_name="Иван Иванов", salary=0)
        assert emp.salary == 0

    def test_invalid_name_one_word(self):
        """
        Тест: ФИО из одного слова отклоняется.
        """
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name="Иван", salary=50000)

    def test_invalid_name_two_words_allowed(self):
        """
        Тест: ФИО из двух слов проходит.
        """
        emp = EmployeeCreate(full_name="Иван Иванов", salary=50000)
        assert emp.full_name == "Иван Иванов"

    def test_invalid_name_three_words(self):
        """
        Тест: ФИО из трёх слов проходит.
        """
        emp = EmployeeCreate(full_name="Иванов Иван Иванович", salary=50000)
        assert emp.full_name == "Иванов Иван Иванович"

    def test_invalid_currency_length(self):
        """
        Тест: валюта неверной длины.
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
    Параметризованный тест: разные комбинации данных.
    """
    if should_pass:
        emp = EmployeeCreate(full_name=full_name, salary=salary)
        assert emp.full_name == full_name
        assert emp.salary == salary
    else:
        with pytest.raises(ValidationError):
            EmployeeCreate(full_name=full_name, salary=salary)
