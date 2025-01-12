import os
import pytest
from unittest.mock import patch, MagicMock
from lib.templates.run_scripts import resolve_and_execute, execute_script


@patch("lib.templates.run_scripts.os.path.isdir")
@patch("lib.templates.run_scripts.os.path.isfile")
@patch("lib.templates.run_scripts.os.listdir")
@patch("lib.templates.run_scripts.execute_script")
@patch("lib.templates.run_scripts.config.scripts_directory", new_callable=lambda: os.path.abspath("/mock/scripts"))
def test_resolve_and_execute_directory(mock_scripts_dir, mock_execute, mock_listdir, mock_isfile, mock_isdir):
    mock_isdir.return_value = True
    mock_listdir.return_value = ["test_script.py"]

    resolve_and_execute("test_script arg1")

    expected_path = os.path.join(mock_scripts_dir, "test_script", "test_script.py")
    mock_execute.assert_called_once_with(expected_path, ["arg1"])


@patch("lib.templates.run_scripts.os.path.isdir")
@patch("lib.templates.run_scripts.os.path.isfile")
@patch("lib.templates.run_scripts.execute_script")
@patch("lib.templates.run_scripts.config.scripts_directory", new_callable=lambda: os.path.abspath("/mock/scripts"))
def test_resolve_and_execute_file(mock_scripts_dir, mock_execute, mock_isfile, mock_isdir):
    mock_isdir.return_value = False
    mock_isfile.return_value = True

    resolve_and_execute("test_script.py arg1")

    expected_path = os.path.join(mock_scripts_dir, "test_script.py")
    mock_execute.assert_called_once_with(expected_path, ["arg1"])


@patch("lib.templates.run_scripts.subprocess.run")
def test_resolve_and_execute_command(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    resolve_and_execute("echo Hello")
    mock_run.assert_called_once_with("echo Hello", shell=True, check=True)
