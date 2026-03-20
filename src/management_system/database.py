"""
Настройка подключения к базе данных.
Используется SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# URL базы данных: создаем файл employees.db в корне проекта
# если файла нет, SQLite создаст его автоматически
SQLALCHEMY_DATABASE_URL = "sqlite:///./employees.db"

# Создаём соединение с БД
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Сессия для работы с БД
SessionLocal = sessionmaker( # pylint: disable=invalid-name
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для всех моделей (от него наследуются все таблицы)
Base = declarative_base()


def init_db() -> None:
    """
    Создаёт все таблицы, определённые в models.py (если их еще нет).
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Генератор сессии для зависимостей.
    Гарантирует закрытие сессии даже при ошибке (паттерн для веб-фреймворков).
    """
    db = SessionLocal()
    try:
        yield db  # type: ignore
    finally:
        db.close()
