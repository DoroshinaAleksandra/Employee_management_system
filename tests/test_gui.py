"""
Tests for the GUI module (NiceGUI interface).
"""
from unittest.mock import Mock, patch

import pytest
from datetime import date

from src.management_system.main import EmployeeApp
from src.management_system.services import EmployeeService
from src.management_system.schemas import EmployeeCreate


def create_context_mock():
    """
    Helper to create a mock that supports context manager protocol.
    Also makes .classes() and .props() return context managers for chained calls.
    """
    mock = Mock()
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=False)
    mock.classes = Mock(return_value=mock)
    mock.props = Mock(return_value=mock)
    return mock


class TestEmployeeAppInitialization:
    """Tests for EmployeeApp class initialization."""

    def test_app_initializes_with_none_session(self):
        """
        Verify that a new application instance starts with empty session attributes.
        """
        app = EmployeeApp()
        
        assert app.db_session is None
        assert app.service is None
        assert app.table_container is None


class TestSessionManagement:
    """Tests for database session management in EmployeeApp."""

    @patch('src.management_system.main.SessionLocal')
    def test_refresh_session_closes_old_session(self, mock_session_local):
        """
        Verify that _refresh_session() closes the old session before creating a new one.
        """
        old_session = Mock()
        new_session = Mock()
        mock_session_local.return_value = new_session
        
        app = EmployeeApp()
        app.db_session = old_session
        app._refresh_session()
        
        old_session.close.assert_called_once()
        mock_session_local.assert_called_once()
        assert app.db_session == new_session
        assert app.service is not None

    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'get_all')
    def test_render_table_shows_empty_message(self, mock_get_all, mock_ui):
        """
        Verify that an empty database shows a user-friendly message.
        """
        mock_get_all.return_value = []

        mock_ui.column.return_value = create_context_mock()
        mock_ui.label.return_value = Mock()
        mock_ui.row.return_value = create_context_mock()

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)
        
        app.table_container = create_context_mock()

        app._render_table()

        mock_ui.label.assert_any_call('База данных пуста. Добавьте первого сотрудника!')
        mock_get_all.assert_called_once()

    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'get_all')
    def test_render_table_clears_container_before_render(self, mock_get_all, mock_ui):
        """
        Verify that table container is cleared before re-rendering to prevent duplicate rows.
        """
        mock_get_all.return_value = []

        mock_ui.column.return_value = create_context_mock()
        mock_ui.label.return_value = Mock()
        mock_ui.row.return_value = create_context_mock()

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)

        app.table_container = create_context_mock()

        app._render_table()

        app.table_container.clear.assert_called_once()


class TestUIStructure:
    """Tests for the main UI layout construction."""

    @patch('src.management_system.main.ui')
    def test_build_ui_creates_header_and_button(self, mock_ui):
        """
        Verify that _build_ui creates the main header and 'Add Employee' button.
        """
        mock_header = create_context_mock()
        mock_header.classes.return_value = mock_header
        mock_ui.header.return_value = mock_header
        
        mock_column = create_context_mock()
        mock_column.classes.return_value = mock_column
        mock_ui.column.return_value = mock_column
        
        mock_row = create_context_mock()
        mock_row.classes.return_value = mock_row
        mock_ui.row.return_value = mock_row
        
        mock_button = Mock()
        mock_button.props.return_value = mock_button
        mock_ui.button.return_value = mock_button
        
        mock_label = Mock()
        mock_label.classes.return_value = mock_label
        mock_ui.label.return_value = mock_label

        app = EmployeeApp()
        
        with patch.object(app, '_render_table'):
            app._build_ui()

        mock_ui.header.assert_called_once()
        mock_ui.button.assert_any_call('Добавить сотрудника', on_click=app._open_create_dialog, icon='add')


class TestDialogs:
    """Tests for dialog interactions (Edit, Delete)."""

    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'get_by_id')
    def test_open_edit_dialog_fetches_employee(self, mock_get_by_id, mock_ui):
        """
        Verify that opening edit dialog fetches employee data by ID.
        """
        mock_emp = Mock()
        mock_emp.full_name = "Иван Иванов"
        mock_emp.id = 1
        mock_emp.position = "Developer"
        mock_emp.salary = 100000
        mock_emp.currency = "RUB"
        mock_emp.timezone = "UTC+3"
        mock_emp.birth_date = None
        mock_emp.hire_date = None
        mock_get_by_id.return_value = mock_emp

        mock_dialog = create_context_mock()
        mock_dialog.open = Mock()
        mock_dialog.close = Mock()
        mock_ui.dialog.return_value = mock_dialog
        
        mock_card = create_context_mock()
        mock_ui.card.return_value = mock_card
        
        mock_input = Mock()
        mock_input.classes.return_value = mock_input
        mock_ui.input.return_value = mock_input
        
        mock_number = Mock()
        mock_number.classes.return_value = mock_number
        mock_ui.number.return_value = mock_number
        
        mock_select = Mock()
        mock_select.classes.return_value = mock_select
        mock_ui.select.return_value = mock_select
        
        mock_date = Mock()
        mock_date.classes.return_value = mock_date
        mock_ui.date.return_value = mock_date
        
        mock_button = Mock()
        mock_button.props.return_value = mock_button
        mock_ui.button.return_value = mock_button
        
        mock_label = Mock()
        mock_label.classes.return_value = mock_label
        mock_ui.label.return_value = mock_label
        
        mock_row = create_context_mock()
        mock_row.classes.return_value = mock_row
        mock_ui.row.return_value = mock_row
        
        mock_column = create_context_mock()
        mock_column.classes.return_value = mock_column
        mock_ui.column.return_value = mock_column

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)

        app._open_edit_dialog(1)

        mock_get_by_id.assert_called_once_with(1)
        mock_ui.dialog.assert_called_once()

    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'get_by_id')
    def test_open_edit_dialog_notifies_if_missing(self, mock_get_by_id, mock_ui):
        """
        Verify that editing non-existent employee shows a warning.
        """
        mock_get_by_id.return_value = None
        mock_ui.notify = Mock()

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)

        app._open_edit_dialog(999)

        mock_ui.notify.assert_called_once_with('Сотрудник не найден', type='warning')
        mock_ui.dialog.assert_not_called()

    @patch('src.management_system.main.ui')
    def test_confirm_delete_opens_dialog(self, mock_ui):
        """
        Verify that delete confirmation dialog opens correctly.
        """
        mock_dialog = create_context_mock()
        mock_dialog.open = Mock()
        mock_dialog.close = Mock()
        mock_ui.dialog.return_value = mock_dialog
        
        mock_card = create_context_mock()
        mock_ui.card.return_value = mock_card
        
        mock_label = Mock()
        mock_label.classes.return_value = mock_label
        mock_ui.label.return_value = mock_label
        
        mock_button = Mock()
        mock_button.props.return_value = mock_button
        mock_ui.button.return_value = mock_button
        
        mock_row = create_context_mock()
        mock_row.classes.return_value = mock_row
        mock_ui.row.return_value = mock_row

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)

        app._confirm_delete(5)

        mock_ui.dialog.assert_called_once()
        mock_ui.label.assert_any_call('Вы уверены?')

    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'delete')
    @patch.object(EmployeeApp, '_render_table')
    def test_delete_callback_calls_service(self, mock_render_table, mock_delete, mock_ui):
        """
        Verify that confirming deletion calls service.delete and refreshes table.
        """
        mock_delete.return_value = True
        mock_ui.notify = Mock()
        
        mock_dialog = create_context_mock()
        mock_dialog.open = Mock()
        mock_dialog.close = Mock()
        mock_ui.dialog.return_value = mock_dialog
        
        mock_card = create_context_mock()
        mock_ui.card.return_value = mock_card
        
        mock_label = Mock()
        mock_label.classes.return_value = mock_label
        mock_ui.label.return_value = mock_label
        
        mock_button = Mock()
        mock_button.props.return_value = mock_button
        mock_ui.button.return_value = mock_button
        
        mock_row = create_context_mock()
        mock_row.classes.return_value = mock_row
        mock_ui.row.return_value = mock_row

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)

        app._confirm_delete(5)
        
        assert mock_ui.dialog.called
        assert mock_delete.called is False
