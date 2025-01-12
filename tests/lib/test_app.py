import pytest
from unittest.mock import MagicMock, patch
import subprocess

import win32con

from lib.position import Position
from lib.layout import Location
from lib.app import AppConfig, LocalAppConfig, App

# Tests for AppConfig
def test_app_config_initialization():
    app_config = AppConfig(path="/mock/path/to/app.exe", default_args=["--arg1"], state=True)
    assert app_config.path == "/mock/path/to/app.exe"
    assert app_config.default_args == ["--arg1"]
    assert app_config.state is True

# Tests for LocalAppConfig
def test_local_app_config_initialization():
    # With location
    location_data = {"row": 0, "col": 0, "row_span": 2, "col_span": 2}
    local_config = LocalAppConfig(app="TestApp", monitor=1, location=location_data, minimize=True)
    assert local_config.app == "TestApp"
    assert local_config.monitor == 0
    assert local_config.location.row == 0
    assert local_config.minimize is True

    # Without location
    local_config = LocalAppConfig(app="TestApp", monitor=1, minimize=False)
    assert local_config.location is None

# Tests for App
def test_app_launch():
    with patch("subprocess.Popen") as mock_popen, \
         patch("lib.app._get_window_handle", return_value=12345), \
         patch("win32gui.ShowWindow") as mock_show_window, \
         patch("win32gui.MoveWindow") as mock_move_window:

        app_config = AppConfig(path="/mock/path/to/app.exe")
        local_config = LocalAppConfig(app="TestApp", monitor=1)
        app = App(app_config, local_config)

        app.launch()

        mock_popen.assert_called_once_with([
            "/mock/path/to/app.exe"
        ], shell=True, creationflags=subprocess.DETACHED_PROCESS)
        mock_show_window.assert_called_once_with(12345, win32con.SW_RESTORE)
        mock_move_window.assert_called_once()

@patch("win32gui.ShowWindow")
@patch("win32gui.MoveWindow")
@patch("win32gui.GetWindowRect", return_value=(100, 100, 500, 400))
def test_move_window(mock_get_window_rect, mock_move_window, mock_show_window):
    app_config = AppConfig(path="/mock/path/to/app.exe", default_position=Position(100, 100, 400, 300))
    local_config = LocalAppConfig(app="TestApp", monitor=1)
    app = App(app_config, local_config)
    app.window_handle = 12345

    app.move_window()

    # Assert that MoveWindow is called with the correct final position
    mock_move_window.assert_called_with(12345, 93, 97, 414, 300, True)
    # Allow multiple calls but verify at least one call
    assert mock_show_window.call_count > 0
    assert mock_move_window.call_count > 0


def test_get_window_position():
    with patch("win32gui.GetWindowRect", return_value=(100, 100, 500, 400)):
        app_config = AppConfig(path="/mock/path/to/app.exe")
        local_config = LocalAppConfig(app="TestApp", monitor=1)
        app = App(app_config, local_config)
        app.window_handle = 12345

        position = app.get_window_position()

        assert position.x == 100
        assert position.y == 100
        assert position.width == 400
        assert position.height == 300

def test_list_all_apps():
    with patch("os.listdir", return_value=["app1.yaml", "app2.yaml"]) as mock_listdir, \
         patch("builtins.open", new_callable=MagicMock) as mock_open, \
         patch("yaml.safe_load", side_effect=[
             {"path": "/mock/app1.exe", "default_args": ["--arg1"]},
             {"path": "/mock/app2.exe", "default_args": ["--arg2"]},
         ]) as mock_safe_load, \
         patch("lib.app.Config") as mock_config:

        mock_config.return_value.apps_directory = "/mock/apps"
        from lib.app import list_all_apps
        list_all_apps()

        mock_listdir.assert_called_once_with("/mock/apps")
        assert mock_open.call_count == 2
        assert mock_safe_load.call_count == 2
