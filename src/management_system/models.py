"""
SQLAlchemy модели для таблицы сотрудников.
"""
from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base


class Employee(Base):  # pylint: disable=too-few-public-methods
    """
    Модель сотрудника для хранения в БД.
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)  # ФИО
    birth_date = Column(Date, nullable=True)  # Дата рождения
    hire_date = Column(Date, nullable=True)  # Дата приёма на работу
    position = Column(String(50), nullable=True)  # Должность
    salary = Column(Float, nullable=False)  # Зарплата
    currency = Column(String(3), default="RUB")  # Валюта (USD, EUR, RUB)
    timezone = Column(String(10), default="UTC+3")  # Часовой пояс

    def __repr__(self):
        return f"<Employee(id={self.id}, name={self.full_name})>"
