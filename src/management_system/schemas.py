"""
Pydantic schemas for input data validation.
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class EmployeeCreate(BaseModel):
    """
    Schema for creating a new employee.
    All fields are validated before writing to the database:
        full_name: minimum 3 characters and 2 words (first + last name)
        salary: cannot be negative
        currency: currency code (RUB/USD/EUR)
        timezone: timezone in UTC±N format
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
        Checks that full_name contains at least 2 words.
        """
        if len(v.split()) < 2:
            raise ValueError('Full name must contain first and last name')
        return v


class EmployeeRead(BaseModel):
    """
    Schema for reading employee data.
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
