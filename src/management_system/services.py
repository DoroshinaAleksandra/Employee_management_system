"""
Service layer for employee operations.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


class EmployeeService:
    """
    Service for CRUD operations on employees.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, employee: schemas.EmployeeCreate) -> models.Employee:
        """
        Creates a new employee and saves to the database.
        Returns the object with assigned ID.
        """
        db_employee = models.Employee(**employee.model_dump())
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def get_all(self) -> List[models.Employee]:
        """
        Returns a list of all employees from the database.
        """
        return self.db.query(models.Employee).all()

    def get_by_id(self, employee_id: int) -> Optional[models.Employee]:
        """
        Finds an employee by unique ID.
        Returns None if not found.
        """
        return self.db.query(models.Employee).filter(
            models.Employee.id == employee_id
        ).first()

    def update(self, employee_id: int,
               employee: schemas.EmployeeCreate) -> Optional[models.Employee]:
        """
        Updates employee fields by ID.
        Returns the updated object or None.
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
         Deletes an employee by ID.
        Returns True if successful, False if not found.
        """
        db_employee = self.get_by_id(employee_id)
        if db_employee:
            self.db.delete(db_employee)
            self.db.commit()
            return True
        return False
