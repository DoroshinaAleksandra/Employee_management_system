"""
Tests for the GUI module (NiceGUI interface).
"""
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import date
from src.management_system.main import EmployeeApp, DatabaseManager, EmployeeTableView, EmployeeDialogManager
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
    
    def test_app_initializes_with_db_manager(self):
        """
        Verify that a new application instance has a DatabaseManager.
        """
        app = EmployeeApp()
        assert app.db_manager is not None
        assert isinstance(app.db_manager, DatabaseManager)
        assert app.table_view is None
        assert app.dialog_manager is None


class TestDatabaseManager:
    """Tests for DatabaseManager class."""
    
    @patch('src.management_system.main.SessionLocal')
    def test_refresh_session_closes_old_session(self, mock_session_local):
        """
        Verify that refresh_session() closes the old session before creating a new one.
        """
        old_session = Mock()
        new_session = Mock()
        mock_session_local.return_value = new_session
        
        db_manager = DatabaseManager()
        db_manager.db_session = old_session
        db_manager.refresh_session()
        
        old_session.close.assert_called_once()
        mock_session_local.assert_called_once()
        assert db_manager.db_session == new_session
        assert db_manager.service is not None
    
    def test_get_service_returns_service(self):
        """
        Verify that get_service() returns the service instance.
        """
        db_manager = DatabaseManager()
        db_manager.service = Mock()
        assert db_manager.get_service() == db_manager.service


class TestEmployeeTableView:
    """Tests for EmployeeTableView class."""
    
    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'get_all')
    def test_render_table_shows_empty_message(self, mock_get_all, mock_ui):
        """
        Verify that an empty database shows a user-friendly message.
        """
        mock_get_all.return_value = []
        
        mock_container = create_context_mock()
        mock_container.clear = Mock()
        
        db_manager = Mock()
        db_manager.get_service().get_all = mock_get_all
        
        table_view = EmployeeTableView(
            container=mock_container,
            db_manager=db_manager,
            on_edit_callback=Mock(),
            on_delete_callback=Mock()
        )
        table_view.render()
        
        mock_ui.label.assert_any_call('База данных пуста. Добавьте первого сотрудника!')
        mock_get_all.assert_called_once()
    
    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'get_all')
    def test_render_table_clears_container_before_render(self, mock_get_all, mock_ui):
        """
        Verify that table container is cleared before re-rendering to prevent duplicate rows.
        """
        mock_get_all.return_value = []
        
        mock_container = create_context_mock()
        mock_container.clear = Mock()
        
        db_manager = Mock()
        db_manager.get_service().get_all = mock_get_all
        
        table_view = EmployeeTableView(
            container=mock_container,
            db_manager=db_manager,
            on_edit_callback=Mock(),
            on_delete_callback=Mock()
        )
        table_view.render()
        
        mock_container.clear.assert_called_once()


class TestEmployeeDialogManager:
    """Tests for EmployeeDialogManager class."""
    
    @patch('src.management_system.main.ui')
    def test_open_edit_dialog_fetches_employee(self, mock_ui):
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
        
        mock_dialog = create_context_mock()
        mock_dialog.open = Mock()
        mock_dialog.close = Mock()
        mock_ui.dialog.return_value = mock_dialog
        mock_ui.card.return_value = create_context_mock()
        mock_ui.input.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.number.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.select.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.date.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.button.return_value = Mock(props=Mock(return_value=Mock()))
        mock_ui.label.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.row.return_value = create_context_mock()
        mock_ui.column.return_value = create_context_mock()

        mock_service = MagicMock(spec=EmployeeService)
        mock_service.get_by_id.return_value = mock_emp
        
        db_manager = Mock()
        db_manager.get_service.return_value = mock_service
        
        dialog_manager = EmployeeDialogManager(
            db_manager=db_manager,
            on_data_changed=Mock()
        )
        dialog_manager.open_edit_dialog(1)
        
        mock_service.get_by_id.assert_called_once_with(1)
        mock_ui.dialog.assert_called_once()
    
    @patch('src.management_system.main.ui')
    def test_open_edit_dialog_notifies_if_missing(self, mock_ui):
        """
        Verify that editing non-existent employee shows a warning.
        """
        mock_ui.notify = Mock()

        mock_service = MagicMock(spec=EmployeeService)
        mock_service.get_by_id.return_value = None
        
        db_manager = Mock()
        db_manager.get_service.return_value = mock_service
        
        dialog_manager = EmployeeDialogManager(
            db_manager=db_manager,
            on_data_changed=Mock()
        )
        dialog_manager.open_edit_dialog(999)
        
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
        mock_ui.card.return_value = create_context_mock()
        mock_ui.label.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.button.return_value = Mock(props=Mock(return_value=Mock()))
        mock_ui.row.return_value = create_context_mock()
        
        db_manager = Mock()
        
        dialog_manager = EmployeeDialogManager(
            db_manager=db_manager,
            on_data_changed=Mock()
        )
        dialog_manager.confirm_delete(5)
        
        mock_ui.dialog.assert_called_once()
        mock_ui.label.assert_any_call('Вы уверены?')
    
    @patch('src.management_system.main.ui')
    @patch.object(EmployeeService, 'delete')
    def test_confirm_delete_does_not_delete_immediately(self, mock_delete, mock_ui):
        """
        Verify that delete confirmation shows dialog first (doesn't delete immediately).
        """
        mock_delete.return_value = True
        mock_ui.notify = Mock()
        
        mock_dialog = create_context_mock()
        mock_dialog.open = Mock()
        mock_dialog.close = Mock()
        mock_ui.dialog.return_value = mock_dialog
        mock_ui.card.return_value = create_context_mock()
        mock_ui.label.return_value = Mock(classes=Mock(return_value=Mock()))
        mock_ui.button.return_value = Mock(props=Mock(return_value=Mock()))
        mock_ui.row.return_value = create_context_mock()
        
        db_manager = Mock()
        
        dialog_manager = EmployeeDialogManager(
            db_manager=db_manager,
            on_data_changed=Mock()
        )
        dialog_manager.confirm_delete(5)
        
        # Dialog should be opened, but delete should NOT be called yet
        # (user must click "Yes" button first)
        assert mock_ui.dialog.called
        assert mock_delete.called is False


class TestEmployeeAppIntegration:
    """Integration tests for EmployeeApp with its components."""
    
    @patch('src.management_system.main.ui')
    def test_build_ui_creates_components(self, mock_ui):
        """
        Verify that _build_ui creates all necessary components.
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
        app.db_manager = Mock()
        
        with patch.object(app, '_render_table'):
            app._build_ui()
        
        mock_ui.header.assert_called_once()
        mock_ui.button.assert_any_call(
            'Добавить сотрудника',
            on_click=app._open_create_dialog,
            icon='add'
        )
        assert app.dialog_manager is not None
        assert app.table_view is not None
    
    def test_render_table_delegates_to_table_view(self):
        """
        Verify that _render_table calls table_view.render().
        """
        app = EmployeeApp()
        app.table_view = Mock()
        app._render_table()
        app.table_view.render.assert_called_once()
    
    def test_open_create_dialog_delegates_to_dialog_manager(self):
        """
        Verify that _open_create_dialog calls dialog_manager.open_create_dialog().
        """
        app = EmployeeApp()
        app.dialog_manager = Mock()
        app._open_create_dialog()
        app.dialog_manager.open_create_dialog.assert_called_once()
    
    def test_open_edit_dialog_delegates_to_dialog_manager(self):
        """
        Verify that _open_edit_dialog calls dialog_manager.open_edit_dialog().
        """
        app = EmployeeApp()
        app.dialog_manager = Mock()
        app._open_edit_dialog(1)
        app.dialog_manager.open_edit_dialog.assert_called_once_with(1)
    
    def test_confirm_delete_delegates_to_dialog_manager(self):
        """
        Verify that _confirm_delete calls dialog_manager.confirm_delete().
        """
        app = EmployeeApp()
        app.dialog_manager = Mock()
        app._confirm_delete(5)
        app.dialog_manager.confirm_delete.assert_called_once_with(5)
