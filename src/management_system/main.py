"""
Временный код для проверки работоспособности всего связанного с БД.
"""
from .database import SessionLocal, init_db
from .schemas import EmployeeCreate
from .services import EmployeeService


def main():
    print("Создаем тестовые данные в базе...\n")

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
        print(f"Добавлен: {created.full_name} ({created.position})")

    db.close()
    print("Тестовые данные сохранены в employees.db.")


if __name__ == "__main__":
    main()

