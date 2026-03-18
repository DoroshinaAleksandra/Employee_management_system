"""
Pydantic схемы для валидации входных данных.
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class EmployeeCreate(BaseModel):
    """
    Схема для создания нового сотрудника.
    Все поля проходят валидацию перед записью в БД:
        full_name: минимум 3 символа и 2 слова (имя + фамилия)
        salary: не может быть отрицательной
        currency: код валюты (RUB/USD/EUR)
        timezone: часовой пояс в формате UTC±N
    """

    full_name: str = Field(..., min_length=3, max_length=100)
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    position: Optional[str] = None
    salary: float = Field(..., ge=0)
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    timezone: str = Field(default="UTC+3", max_length=10)

    @field_validator('full_name')
    @classmethod
    def check_name_has_parts(cls, v) -> str:
        """
        Проверяет, что ФИО содержит минимум 2 слова.
        """
        if len(v.split()) < 2:
            raise ValueError('ФИО должно содержать имя и фамилию (отчество при наличии)')
        return v


class EmployeeRead(BaseModel):
    """
    Схема для чтения данных сотрудника.
    """

    id: int
    full_name: str
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    position: Optional[str] = None
    salary: float
    currency: str
    timezone: str
    model_config = ConfigDict(from_attributes=True)
