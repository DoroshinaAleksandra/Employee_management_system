"""
Temporary code for testing database functionality.
"""
from .database import SessionLocal, init_db
from .schemas import EmployeeCreate
from .services import EmployeeService


def main():
    """
    Creates demo employees and saves them to the database.
    """
    print("Creating test data in database...\n")

    init_db()

    db = SessionLocal()
    service = EmployeeService(db)

    demo_employees = [
        EmployeeCreate(full_name="Иван Иванов", salary=50000, position="Разработчик"),
        EmployeeCreate(full_name="Анна Петрова", salary=75000, position="Team Lead"),
        EmployeeCreate(full_name="Сергей Сидоров", salary=60000, position="QA Engineer"),
    ]

    for emp_data in demo_employees:
        created = service.create(emp_data)
        print(f"Added: {created.full_name} ({created.position})")

    db.close()
    print("Test data saved to employees.db.")


if __name__ == "__main__":
    main()
