from datetime import date
from typing import Optional
from nicegui import ui
from sqlalchemy.orm import Session

from management_system.database import init_db, SessionLocal
from management_system.schemas import EmployeeCreate
from management_system.services import EmployeeService
from management_system.constants import (
    CURRENCIES,
    TIMEZONES,
    DEFAULT_CURRENCY,
    DEFAULT_TIMEZONE,
)


class ValidationError(Exception):
    """There is error in validating the data"""
    pass


class EmployeeApp:
    """
    Builds an interface for the app.
    """

    def __init__(self):
        self.db_session: Optional[Session] = None
        self.service: Optional[EmployeeService] = None
        self.table_container = None

    def initialize_db(self):
        init_db()
        self._refresh_session()

    def _refresh_session(self):
        if self.db_session:
            self.db_session.close()
        self.db_session = SessionLocal()
        self.service = EmployeeService(self.db_session)

    def run(self):
        self.initialize_db()
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
        Builds the main user interface layout.
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

            self._render_table()

    def _render_table(self):
        """
        Renders the employee table with all records from the database.
        """
        self._refresh_session()
        employees = self.service.get_all()

        self.table_container.clear()

        if not employees:
            with self.table_container:
                ui.label('База данных пуста. Добавьте первого сотрудника!').classes(
                    'text-grey-7 text-center q-pa-md text-h6')
            return

        with self.table_container:
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
                                      on_click=lambda e, eid=emp.id: self._open_edit_dialog(eid)
                                      ).props('flat color=blue size=sm')
                            ui.button('Удалить',
                                      on_click=lambda e, eid=emp.id: self._confirm_delete(eid)
                                      ).props('flat color=red size=sm')

    def _open_create_dialog(self):
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
                inp_salary = ui.number(label='Зарплата', value=0.0, format='%.2f').classes('col-grow')
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
                            birth_date=date.fromisoformat(dt_birth.value) if dt_birth.value else None,
                            hire_date=date.fromisoformat(dt_hire.value) if dt_hire.value else None,
                        )
                        self._refresh_session()
                        self.service.create(data)
                        ui.notify('Сотрудник успешно добавлен!', type='positive', icon='check')
                        dialog.close()
                        self._render_table()
                    except ValidationError as e:
                        ui.notify(f'Ошибка данных: {str(e)}', type='negative', icon='error')

                ui.button('Создать', on_click=save_new).props('color=primary')

        dialog.open()

    def _open_edit_dialog(self, emp_id: int):
        """
        Opens the dialog for editing an existing employee.

        Args: emp_id: The ID of the employee to edit.
        """
        self._refresh_session()
        if not isinstance(self.service, EmployeeService):
            ui.notify('Проблемы с сервисом', type='negative', icon='error')
            return
        emp = self.service.get_by_id(emp_id)
        if not emp:
            ui.notify('Сотрудник не найден', type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
            ui.label(f'Редактирование: {emp.full_name}').classes('text-h6 q-mb-md text-primary')

            inp_name = ui.input(label='ФИО', value=str(emp.full_name)).classes('w-full')
            inp_pos = ui.input(label='Должность', value=str(emp.position or '')).classes('w-full')

            with ui.row().classes('w-full gap-2'):
                inp_salary = ui.number(label='Зарплата', value=float(emp.salary), format='%.2f').classes('col-grow')
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
                            birth_date=date.fromisoformat(dt_birth.value) if dt_birth.value else None,
                            hire_date=date.fromisoformat(dt_hire.value) if dt_hire.value else None,
                        )
                        self._refresh_session()
                        updated = self.service.update(emp_id, data)
                        if updated:
                            ui.notify('Данные обновлены!', type='positive', icon='check')
                            dialog.close()
                            self._render_table()
                        else:
                            ui.notify('Не удалось обновить', type='negative')
                    except ValidationError as e:
                        ui.notify(f'Ошибка данных: {str(e)}', type='negative', icon='error')

                ui.button('Сохранить', on_click=save_changes).props('color=primary')

        dialog.open()

    def _confirm_delete(self, emp_id: int):
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
                    self._refresh_session()
                    if self.service.delete(emp_id):
                        ui.notify('Сотрудник удален', type='info', icon='delete')
                        self._render_table()
                    else:
                        ui.notify('Ошибка при удалении', type='negative')
                    dialog.close()

                ui.button('Да, удалить', on_click=do_delete).props('color=red flat')

        dialog.open()


if __name__ == "__main__":
    app = EmployeeApp()
    app.run()
