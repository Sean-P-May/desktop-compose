import pytest
from unittest.mock import patch, MagicMock, mock_open
import yaml
from lib.layout import Layout
from lib.templates.template import Template, load_apps  # Replace 'your_module' with the actual module name


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    apps_yaml = [
        {
            "app": "test_app",
            "monitor": 1,
            "location": {"row": 0, "col": 0, "row_span": 2, "col_span": 2},
        }
    ]
    layout_dicts = [
        {"rows": 3, "cols": 3},
        {"rows": 2, "cols": 4}
    ]
    template = Template(
        name="TestTemplate",
        file_path="/tmp/test_template.yaml",
        description="A test template",
        apps=apps_yaml,
        layout=layout_dicts,  # These will be converted to Layout objects in __init__
        before_scripts=["echo 'Before'"],
        after_scripts=["echo 'After'"],
    )
    return apps_yaml, layout_dicts, template



def test_layout_conversion(sample_data):
    """Test that layout dictionaries are converted to Layout objects."""
    _, layout_dicts, template = sample_data

    assert len(template.layouts) == len(layout_dicts)
    for layout, layout_dict in zip(template.layouts, layout_dicts):
        assert isinstance(layout, Layout)
        assert layout.rows == layout_dict["rows"]
        assert layout.cols == layout_dict["cols"]


def test_monitor_assignment(sample_data):
    """Test that layouts are assigned to monitors by index."""
    _, _, template = sample_data

    monitors = []
    for index, layout in enumerate(template.layouts):
        monitors.append({"monitor": index, "layout": layout})

    assert len(monitors) == len(template.layouts)
    for index, monitor in enumerate(monitors):
        assert monitor["monitor"] == index
        assert monitor["layout"] == template.layouts[index]


@patch("pyvda.VirtualDesktop.create")
@patch("pyvda.VirtualDesktop.rename")
@patch("pyvda.VirtualDesktop.go")
def test_launch(mock_go, mock_rename, mock_create, sample_data):
    """Test the launch method."""
    _, _, template = sample_data
    mock_desktop = MagicMock()
    mock_create.return_value = mock_desktop

    template.launch()

    mock_create.assert_called_once()
    mock_desktop.rename.assert_called_once_with("TestTemplate")
    mock_desktop.go.assert_called_once()


@patch("os.path.join", return_value="/tmp/test_template.yaml")
@patch("builtins.open", new_callable=mock_open)
def test_save(mock_open, mock_join, sample_data):
    """Test saving a template to a YAML file."""
    _, _, template = sample_data

    template.save()

    mock_open.assert_called_once_with("/tmp/test_template.yaml", "w")
    mock_open().write.assert_called_once()
    written_data = yaml.safe_load(mock_open().write.call_args[0][0])

    # Check serialized data
    assert written_data["name"] == "TestTemplate"
    assert len(written_data["layout"]) == len(template.layouts)
    for layout_dict, layout in zip(written_data["layout"], template.layouts):
        assert layout_dict["rows"] == layout.rows
        assert layout_dict["cols"] == layout.cols

