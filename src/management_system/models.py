"""
SQLAlchemy models for the employees table.
"""
from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base


class Employee(Base):  # pylint: disable=too-few-public-methods
    """
    Employee model for database storage.
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)  # Full name
    birth_date = Column(Date, nullable=True)  # Date of birth
    hire_date = Column(Date, nullable=True)  # Hire date
    position = Column(String(50), nullable=True)  # Position / Job title
    salary = Column(Float, nullable=False)  # Salary
    currency = Column(String(3), default="RUB")  # Currency code (USD, EUR, RUB)
    timezone = Column(String(10), default="UTC+3")  # Timezone offset

    def __repr__(self):
        return f"<Employee(id={self.id}, name={self.full_name})>"
