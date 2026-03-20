"""
Сервисный слой для работы с сотрудниками.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


class EmployeeService:
    """
    Сервис для CRUD-операций с сотрудниками.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, employee: schemas.EmployeeCreate) -> models.Employee:
        """
        Создаёт нового сотрудника и сохраняет в БД.
        Возвращает объект с присвоенным ID.
        """
        db_employee = models.Employee(**employee.model_dump())
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def get_all(self) -> List[models.Employee]:
        """
        Возвращает список всех сотрудников из базы данных.
        """
        return self.db.query(models.Employee).all()

    def get_by_id(self, employee_id: int) -> Optional[models.Employee]:
        """
        Находит сотрудника по уникальному ID.
        Возвращает None, если не найден.
        """
        return self.db.query(models.Employee).filter(
            models.Employee.id == employee_id
        ).first()

    def update(self, employee_id: int,
               employee: schemas.EmployeeCreate) -> Optional[models.Employee]:
        """
        Обновляет поля сотрудника по ID.
        Возвращает обновлённый объект или None.
        """
        db_employee = self.get_by_id(employee_id)
        if db_employee:
            for key, value in employee.model_dump().items():
                setattr(db_employee, key, value)
            self.db.commit()
            self.db.refresh(db_employee)
        return db_employee

    def delete(self, employee_id: int) -> bool:
        """
        Удаляет сотрудника по ID.
        Возвращает True если успешно, False если не найден.
        """
        db_employee = self.get_by_id(employee_id)
        if db_employee:
            self.db.delete(db_employee)
            self.db.commit()
            return True
        return False
