import os
import pytest
from unittest.mock import patch, mock_open
from lib.config import Config, ConfigKeys
import yaml

# Tests for Config class
def test_initialize_config_creates_default():
    with patch("os.path.exists", return_value=False) as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("lib.config.Config.write_yaml") as mock_write_yaml:

        config = Config()

        mock_exists.assert_called_with(config.config_file)
        mock_makedirs.assert_any_call(config.apps_directory, exist_ok=True)
        mock_makedirs.assert_any_call(config.templates_directory, exist_ok=True)
        mock_write_yaml.assert_called_once()

def test_initialize_config_loads_existing():
    with patch("os.path.exists", return_value=True) as mock_exists, \
         patch("builtins.open", mock_open(read_data="""
            apps_directory: /mock/apps
            templates_directory: /mock/templates
            zone_configs_directory: /mock/zones
            default_text_editor: vim
            global_configs_directory: /mock/globals.yaml
        """)) as mock_file, \
         patch("os.makedirs") as mock_makedirs:

        config = Config()

        mock_exists.assert_called_with(config.config_file)
        assert config.apps_directory == "/mock/apps"
        assert config.templates_directory == "/mock/templates"
        assert config.zone_configs_directory == "/mock/zones"
        assert config.default_text_editor == "vim"
        assert config.global_variables_file == "/mock/globals.yaml"

def test_handle_yaml_error():
    with patch("builtins.exit") as mock_exit:
        error = yaml.YAMLError()
        config = Config()
        config.handle_yaml_error(error)
        mock_exit.assert_called_once_with(1)

def test_create_default_config():
    with patch("os.makedirs") as mock_makedirs, \
         patch("lib.config.Config.write_yaml") as mock_write_yaml:

        config = Config()
        config.create_default_config()

        mock_makedirs.assert_any_call(config.apps_directory, exist_ok=True)
        mock_makedirs.assert_any_call(config.templates_directory, exist_ok=True)
        mock_write_yaml.assert_called_once_with(config.config_file, {
            ConfigKeys.APPS_DIRECTORY.value: config.apps_directory,
            ConfigKeys.TEMPLATES_DIRECTORY.value: config.templates_directory,
            ConfigKeys.ZONE_CONFIGS_DIRECTORY.value: config.zone_configs_directory,
            ConfigKeys.SCRIPTS_DIRECTORY.value: config.scripts_directory,
            ConfigKeys.DEFAULT_TEXT_EDITOR.value: config.default_text_editor,
            ConfigKeys.GLOBAL_CONFIGS_DIRECTORY.value: config.global_variables_file,
        })

def test_ensure_directories():
    with patch("os.makedirs") as mock_makedirs:
        config = Config()
        config.ensure_directories()

        mock_makedirs.assert_any_call(config.apps_directory, exist_ok=True)
        mock_makedirs.assert_any_call(config.templates_directory, exist_ok=True)
        mock_makedirs.assert_any_call(config.zone_configs_directory, exist_ok=True)
        mock_makedirs.assert_any_call(config.scripts_directory, exist_ok=True)

@patch("yaml.dump")  # Mock yaml.dump
@patch("builtins.open", new_callable=mock_open)  # Mock file open
def test_write_yaml(mock_open, mock_yaml_dump):
    data = {"key": "value"}
    Config.write_yaml("/mock/config.yaml", data)

    # Ensure the file was opened in write mode
    mock_open.assert_called_once_with("/mock/config.yaml", "w")

    # Verify `yaml.dump` was called with expected arguments
    mock_yaml_dump.assert_called_once_with(data, mock_open(), default_flow_style=False, sort_keys=False)


def test_get_error_line_number():
    error = yaml.YAMLError()
    error.problem_mark = type("", (), {"line": 5})()  # Mocking a problem_mark

    config = Config()
    line_number = config.get_error_line_number(error)

    assert line_number == 6
