"""
Employee Management System - Main GUI Module.

This module provides the main application interface for managing employee records.
It uses NiceGUI for the web-based user interface and SQLAlchemy for database operations.
"""

from datetime import date
from typing import Optional

import pydantic
from nicegui import ui
from sqlalchemy.orm import Session

from .constants import (CURRENCIES, DEFAULT_CURRENCY, DEFAULT_TIMEZONE,
                        TIMEZONES)
from .database import SessionLocal, init_db
from .schemas import EmployeeCreate
from .services import EmployeeService


class DatabaseManager:
    """
    Manages database connections and sessions.
    """

    def __init__(self):
        """
        Initialize the DatabaseManager.
        
        Sets up initial state with no active session or service.
        Call initialize_db() before using to establish connection.
        """
        self.db_session: Optional[Session] = None
        self.service: Optional[EmployeeService] = None

    def initialize_db(self):
        """
        Initialize the database and create the first session.
        
        This method should be called once at application startup.
        It runs database migrations and establishes the initial session.
        """
        init_db()
        self.refresh_session()

    def refresh_session(self):
        """
        Create a new database session, closing any existing one.
        
        Closes the current session if it exists to prevent resource leaks,
        then creates a fresh session and initializes the EmployeeService.
        Call this before database operations to ensure a valid connection.
        """
        if self.db_session:
            self.db_session.close()
        self.db_session = SessionLocal()
        self.service = EmployeeService(self.db_session)

    def get_service(self):
        """
        Get the EmployeeService instance for data operations.
        """
        return self.service


class EmployeeTableView:  # pylint: disable=too-few-public-methods
    """
    Displays the table with employees.
    """

    def __init__(self, container, db_manager, on_edit_callback, on_delete_callback):
        self.container = container
        self.db_manager = db_manager
        self.on_edit_callback = on_edit_callback
        self.on_delete_callback = on_delete_callback

    def render(self):
        """
        Renders the employee table with all records from the database.
        """
        self.db_manager.refresh_session()
        employees = self.db_manager.get_service().get_all()

        self.container.clear()

        if not employees:
            with self.container:
                ui.label('База данных пуста. Добавьте первого сотрудника!').classes(
                    'text-grey-7 text-center q-pa-md text-h6')
            return

        with self.container:
            with ui.row().classes('w-full bg-grey-3 q-pa-sm rounded-top font-bold'):
                ui.label('ID').classes('col-1')
                ui.label('ФИО').classes('col-2')
                ui.label('Должность').classes('col-1')
                ui.label('Зарплата').classes('col-1 text-right')
                ui.label('Дата рождения').classes('col-1 text-center').tooltip('Формат: DD.MM.YYYY')
                ui.label('Принят').classes('col-1 text-center').tooltip('Формат: DD.MM.YYYY')
                ui.label('Действия').classes('col-1 text-center')

            for emp in employees:
                with ui.row().classes('w-full bg-white q-pa-sm border-bottom items-center'):
                    ui.label(str(emp.id)).classes('col-1')
                    ui.label(emp.full_name).classes('col-2')
                    ui.label(emp.position or '—').classes('col-1')
                    ui.label(f'{emp.salary:,.2f} {emp.currency}').classes('col-1 text-right')

                    birth = emp.birth_date.strftime('%d.%m.%Y') if emp.birth_date else '—'
                    ui.label(birth).classes('col-1 text-center')

                    hire = emp.hire_date.strftime('%d.%m.%Y') if emp.hire_date else '—'
                    ui.label(hire).classes('col-1 text-center')

                    with ui.column().classes('col-1'):
                        with ui.row().classes('gap-1 justify-center'):
                            ui.button('Редактировать',
                                      on_click=lambda e, eid=emp.id: self.on_edit_callback(eid)
                                      ).props('flat color=blue size=sm')
                            ui.button('Удалить',
                                      on_click=lambda e, eid=emp.id: self.on_delete_callback(eid)
                                      ).props('flat color=red size=sm')


class EmployeeDialogManager:
    """
    Manages all dialog windows (Create, Edit, Delete).
    """

    def __init__(self, db_manager, on_data_changed):
        self.db_manager = db_manager
        self.on_data_changed = on_data_changed

    def open_create_dialog(self):
        """
        Opens the dialog for creating a new employee.
        """
        with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
            ui.label('Новый сотрудник').classes('text-h6 q-mb-md text-primary')

            inp_name = ui.input(
                label='ФИО (Фамилия Имя Отчество)',
                validation={'Минимум 2 слова': lambda v: len(v.split()) >= 2}
            ).classes('w-full')

            inp_pos = ui.input(label='Должность').classes('w-full')

            with ui.row().classes('w-full gap-2'):
                inp_salary = ui.number(label='Зарплата', value=0.0,
                                       format='%.2f').classes('col-grow')
                sel_currency = ui.select(
                    options=CURRENCIES,
                    label='Валюта',
                    value=DEFAULT_CURRENCY
                ).classes('col-4')
                sel_tz = ui.select(
                    options=TIMEZONES,
                    label='Часовой пояс',
                    value=DEFAULT_TIMEZONE
                ).classes('col-4')

            with ui.row().classes('w-full gap-2'):
                with ui.column().classes('col-grow'):
                    ui.label('Дата рождения').classes('text-sm text-grey-7')
                    dt_birth = ui.date(mask='YYYY-MM-DD').classes('w-full')
                with ui.column().classes('col-grow'):
                    ui.label('Дата приема').classes('text-sm text-grey-7')
                    dt_hire = ui.date(mask='YYYY-MM-DD').classes('w-full')

            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('Отмена', on_click=dialog.close).props('outline')

                def save_new():
                    try:
                        data = EmployeeCreate(
                            full_name=inp_name.value,
                            position=inp_pos.value or None,
                            salary=inp_salary.value,
                            currency=sel_currency.value,
                            timezone=sel_tz.value,
                            birth_date=(date.fromisoformat(dt_birth.value)
                                        if dt_birth.value else None),
                            hire_date=date.fromisoformat(dt_hire.value) if dt_hire.value else None,
                        )
                        self.db_manager.refresh_session()
                        self.db_manager.get_service().create(data)
                        ui.notify('Сотрудник успешно добавлен!', type='positive', icon='check')
                        dialog.close()
                        self.on_data_changed()
                    except pydantic.ValidationError as e:
                        ui.notify(f'Ошибка данных: {str(e)}', type='negative', icon='error')

                ui.button('Создать', on_click=save_new).props('color=primary')

        dialog.open()

    def open_edit_dialog(self, emp_id):
        """
        Opens the dialog for editing an existing employee.

        Args: emp_id: The ID of the employee to edit.
        """
        self.db_manager.refresh_session()

        if not isinstance(self.db_manager.get_service(), EmployeeService):
            ui.notify('Проблемы с сервисом', type='negative', icon='error')
            return
        emp = self.db_manager.get_service().get_by_id(emp_id)
        if not emp:
            ui.notify('Сотрудник не найден', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
            ui.label(f'Редактирование: {emp.full_name}').classes('text-h6 q-mb-md text-primary')

            inp_name = ui.input(label='ФИО', value=str(emp.full_name)).classes('w-full')
            inp_pos = ui.input(label='Должность', value=str(emp.position or '')).classes('w-full')

            with ui.row().classes('w-full gap-2'):
                inp_salary = ui.number(label='Зарплата',
                                       value=float(emp.salary), format='%.2f').classes('col-grow')
                sel_currency = ui.select(
                    options=CURRENCIES,
                    label='Валюта',
                    value=emp.currency
                ).classes('col-4')
                sel_tz = ui.select(
                    options=TIMEZONES,
                    label='Часовой пояс',
                    value=emp.timezone
                ).classes('col-4')

            val_birth = emp.birth_date.isoformat() if emp.birth_date else ''
            val_hire = emp.hire_date.isoformat() if emp.hire_date else ''

            with ui.column().classes('col-grow'):
                ui.label('Дата рождения').classes('text-sm text-grey-7')
                dt_birth = ui.date(value=val_birth, mask='YYYY-MM-DD').classes('w-full')
            with ui.column().classes('col-grow'):
                ui.label('Дата приема').classes('text-sm text-grey-7')
                dt_hire = ui.date(value=val_hire, mask='YYYY-MM-DD').classes('w-full')

            with ui.row().classes('w-full justify-end q-mt-md'):
                ui.button('Отмена', on_click=dialog.close).props('outline')

                def save_changes():
                    try:
                        data = EmployeeCreate(
                            full_name=inp_name.value,
                            position=inp_pos.value or None,
                            salary=inp_salary.value,
                            currency=sel_currency.value,
                            timezone=sel_tz.value,
                            birth_date=(date.fromisoformat(dt_birth.value)
                                        if dt_birth.value else None),
                            hire_date=date.fromisoformat(dt_hire.value) if dt_hire.value else None,
                        )
                        self.db_manager.refresh_session()
                        updated = self.db_manager.get_service().update(emp_id, data)
                        if updated:
                            ui.notify('Данные обновлены!', type='positive', icon='check')
                            dialog.close()
                            self.on_data_changed()
                        else:
                            ui.notify('Не удалось обновить', type='negative')
                    except pydantic.ValidationError as e:
                        ui.notify(f'Ошибка данных: {str(e)}', type='negative', icon='error')

                ui.button('Сохранить', on_click=save_changes).props('color=primary')

        dialog.open()

    def confirm_delete(self, emp_id):
        """
        Open confirmation dialog for deleting an employee.

        Args: emp_id: The ID of the employee to delete.
        """
        with ui.dialog() as dialog, ui.card().classes('p-4'):
            ui.label('Вы уверены?').classes('text-h6')
            ui.label('Это действие нельзя отменить.').classes('text-grey-7')

            with ui.row().classes('justify-end q-mt-md'):
                ui.button('Нет', on_click=dialog.close).props('outline')

                def do_delete():
                    self.db_manager.refresh_session()
                    if self.db_manager.get_service().delete(emp_id):
                        ui.notify('Сотрудник удален', type='info', icon='delete')
                        self.on_data_changed()
                    else:
                        ui.notify('Ошибка при удалении', type='negative')
                    dialog.close()

                ui.button('Да, удалить', on_click=do_delete).props('color=red flat')

        dialog.open()


class EmployeeApp:  # pylint: disable=too-few-public-methods
    """
    Builds an interface for the app.
    """

    def __init__(self):
        """
        Initialize the EmployeeApp.
        
        Creates a DatabaseManager instance and sets component references
        to None. Components (table_view, dialog_manager) are initialized
        in _build_ui() after the database is ready.
        """
        self.db_manager = DatabaseManager()
        self.table_view = None
        self.dialog_manager = None
        self.table_container = None

    def run(self):
        """
        Start the application.
        
        Initializes the database, builds the user interface, and launches
        the NiceGUI server. This is the main entry point for running the app.
        Server runs on localhost:8080 without auto-reload.
        """
        self.db_manager.initialize_db()
        self._build_ui()
        ui.run(
            title="Система управления сотрудниками",
            host='127.0.0.1',
            port=8080,
            reload=False,
            reconnect_timeout=0
        )

    def _build_ui(self):
        """
        Build the main user interface layout.
        
        Creates the header, title, 'Add Employee' button, and initializes
        the table container. Also instantiates EmployeeDialogManager and
        EmployeeTableView with appropriate callbacks for user interactions.
        Finally renders the initial employee table.
        """
        with ui.header().classes('items-center justify-between'):
            ui.label('Management System').classes('text-h6 font-bold')

        with ui.column().classes('w-full items-center q-pa-md'):
            ui.label('Управление персоналом').classes('text-h4 q-mb-md')

            with ui.row().classes('w-full max-w-4xl justify-between items-center q-mb-lg'):
                ui.button(
                    'Добавить сотрудника',
                    on_click=self._open_create_dialog,
                    icon='add'
                ).props('color=primary size=lg')

            self.table_container = ui.column().classes('w-full max-w-4xl')

            self.dialog_manager = EmployeeDialogManager(
                db_manager=self.db_manager,
                on_data_changed=self._render_table
            )

            self.table_view = EmployeeTableView(
                container=self.table_container,
                db_manager=self.db_manager,
                on_edit_callback=self._open_edit_dialog,
                on_delete_callback=self._confirm_delete
            )

            self._render_table()

    def _render_table(self):
        """
        Render the employee table by delegating to EmployeeTableView.
        
        Calls the table_view.render() method if it exists. This method
        is used as a callback when data changes (create, update, delete)
        to refresh the displayed employee list.
        """
        if self.table_view:
            self.table_view.render()

    def _open_create_dialog(self):
        """
        Open the create employee dialog.
        
        Delegates to EmployeeDialogManager.open_create_dialog() if the
        dialog manager is initialized. Called when user clicks the
        'Add Employee' button.
        """
        if self.dialog_manager:
            self.dialog_manager.open_create_dialog()

    def _open_edit_dialog(self, emp_id):
        """
        Open the edit employee dialog for a specific employee.
        
        Args:
            emp_id: The ID of the employee to edit.
        """
        if self.dialog_manager:
            self.dialog_manager.open_edit_dialog(emp_id)

    def _confirm_delete(self, emp_id):
        """
        Open the delete confirmation dialog for a specific employee.
        
        Args:
            emp_id: The ID of the employee to delete.
        """
        if self.dialog_manager:
            self.dialog_manager.confirm_delete(emp_id)


if __name__ == "__main__":
    app = EmployeeApp()
    app.run()
