"""
Tests for the GUI module (NiceGUI interface).
"""
from unittest.mock import Mock, patch

import pytest
from datetime import date

from src.management_system.main import EmployeeApp
from src.management_system.services import EmployeeService


class TestEmployeeAppInitialization:
    """Tests for EmployeeApp class initialization."""

    def test_app_initializes_with_none_session(self):
        """
        Verify that a new application instance starts with empty session attributes.
        
        This ensures no resource leaks occur before the app is fully initialized.
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
        
        This prevents resource leaks and ensures clean database connections.
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
        
        This tests UI feedback, not data retrieval.
        """

        # Mock service method to avoid database query
        mock_get_all.return_value = []

        mock_ui.column.return_value = Mock()
        mock_ui.label.return_value = Mock()
        mock_ui.row.return_value = Mock()

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)
        
        # Mock table_container with context manager support
        app.table_container = Mock()
        app.table_container.__enter__ = Mock(return_value=app.table_container)
        app.table_container.__exit__ = Mock(return_value=False)

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

        mock_ui.column.return_value = Mock()
        mock_ui.label.return_value = Mock()
        mock_ui.row.return_value = Mock()

        app = EmployeeApp()
        app.db_session = Mock()
        app.service = EmployeeService(app.db_session)

        app.table_container = Mock()
        app.table_container.__enter__ = Mock(return_value=app.table_container)
        app.table_container.__exit__ = Mock(return_value=False)

        app._render_table()

        app.table_container.clear.assert_called_once()
