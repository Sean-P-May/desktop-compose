import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
from lib.templates.template import Template
from lib.templates.template_management import (
    save_template,
    get_template_by_full_path,
    get_template_by_file_name,
    get_all_templates,
    get_template_by_name,
    get_template,
    list_templates,
)


@pytest.fixture
def mock_config():
    with patch("lib.templates.template_management.config") as mock_config:
        mock_config.templates_directory = "/mock/templates"
        mock_config.global_variables_file = "/mock/global_vars.yaml"
        yield mock_config


@patch("os.path.exists", return_value=False)
@patch("lib.templates.template.Template.save")
def test_save_template(mock_save, mock_exists):
    template = Template(
        name="Original",
        file_path="/mock/original.yaml",
        description="Test",
        layout=[{"rows": 3, "cols": 3}],  # Provide a valid layout
    )

    save_template(template, "NewName", "/mock/new_template.yaml")

    assert template.name == "NewName"
    assert template.file_name == "/mock/new_template.yaml"
    mock_save.assert_called_once()


@patch("builtins.open", new_callable=mock_open, read_data="name: TestTemplate\nlayout:\n  - rows: 3\n    cols: 3\n")
@patch("os.path.isabs", return_value=True)
def test_get_template_by_full_path(mock_isabs, mock_open):
    template = get_template_by_full_path("/mock/templates/template.yaml")

    assert template.name == "TestTemplate"
    assert len(template.layouts) == 1
    assert template.layouts[0].rows == 3
    assert template.layouts[0].cols == 3
    mock_open.assert_called_once_with("/mock/templates/template.yaml")


@patch("os.listdir", return_value=["template1.yaml", "template2.yaml"])
@patch("lib.templates.template_management.get_template_by_file_name")
def test_get_all_templates(mock_get_template_by_file_name, mock_listdir, mock_config):
    mock_get_template_by_file_name.side_effect = [
        Template(name="Template1", file_path="/mock/templates/template1.yaml", layout=[{"rows": 3, "cols": 3}]),
        Template(name="Template2", file_path="/mock/templates/template2.yaml", layout=[{"rows": 2, "cols": 4}]),
    ]

    templates = get_all_templates()

    assert len(templates) == 2
    assert templates[0].name == "Template1"
    assert templates[1].name == "Template2"
    assert templates[0].layouts[0].rows == 3
    assert templates[1].layouts[0].cols == 4


@patch("lib.templates.template_management.get_all_templates")
def test_get_template_by_name(mock_get_all_templates):
    mock_get_all_templates.return_value = [
        Template(name="Template1", file_path="/mock/templates/template1.yaml", layout=[{"rows": 3, "cols": 3}]),
        Template(name="Template2", file_path="/mock/templates/template2.yaml", layout=[{"rows": 2, "cols": 4}]),
    ]

    template = get_template_by_name("Template2")

    assert template.name == "Template2"
    assert template.layouts[0].rows == 2


@patch("lib.templates.template_management.get_template_by_full_path")
@patch("lib.templates.template_management.get_template_by_file_name")
@patch("lib.templates.template_management.get_template_by_name")
def test_get_template(mock_get_by_name, mock_get_by_file, mock_get_by_path):
    mock_get_by_path.return_value = Template(name="TemplateByPath", file_path="/mock/templates/path.yaml", layout=[{"rows": 3, "cols": 3}])
    mock_get_by_file.return_value = Template(name="TemplateByFile", file_path="/mock/templates/file.yaml", layout=[{"rows": 2, "cols": 2}])
    mock_get_by_name.return_value = Template(name="TemplateByName", file_path="/mock/templates/name.yaml", layout=[{"rows": 4, "cols": 4}])

    template = get_template("/mock/templates/path.yaml")
    assert template.name == "TemplateByPath"
    assert template.layouts[0].rows == 3

    template = get_template("file.yaml")
    assert template.name == "TemplateByFile"
    assert template.layouts[0].cols == 2

    template = get_template("TemplateByName")
    assert template.name == "TemplateByName"
    assert template.layouts[0].rows == 4


@patch("lib.templates.template_management.get_all_templates")
def test_list_templates(mock_get_all_templates, capsys):
    mock_get_all_templates.return_value = [
        Template(name="Template1", file_path="/mock/templates/template1.yaml", layout=[{"rows": 3, "cols": 3}]),
        Template(name="Template2", file_path="/mock/templates/template2.yaml", layout=[{"rows": 2, "cols": 4}]),
    ]

    list_templates()

    captured = capsys.readouterr()
    assert "Template1" in captured.out
    assert "Template2" in captured.out