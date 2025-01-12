import pytest
import yaml
from unittest.mock import mock_open, patch

# We import from this file itself (or adjust your import path as needed)
# from lib.templates.parse_variables import parse_variables
# In this single-file example, parse_variables is already defined above:
from lib.templates.parse_variables import parse_variables


@pytest.fixture
def global_variables_file(tmp_path):
    """
    Fixture to create a temporary global variables file.
    """
    file_path = tmp_path / "global_variables.yaml"
    content = """
    ROOT: "/base"
    """
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def raw_yaml():
    """
    Fixture for a typical YAML input with placeholders.
    Used by tests that expect all placeholders to be resolvable in the raw.
    """
    return """
    variables:
      PATH: "<ROOT>/dir/<SUBDIR>"
      ROOT: "/base"
      SUBDIR: "<YEAR>/<MONTH>"
      YEAR: "2023"
      MONTH: "October"
    """


@pytest.fixture
def raw_yaml_unresolved():
    """
    A special fixture that does NOT define SUBDIR, so that SUBDIR remains unresolved
    if not provided locally/globally.
    """
    return """
    variables:
      PATH: "<ROOT>/dir/<SUBDIR>"
      ROOT: "/base"
      YEAR: "2023"
      MONTH: "October"
    """


@pytest.fixture
def large_yaml():
    """
    Fixture for a large and complex YAML with nested placeholders.
    """
    return """
    variables:
      PATH: "<ROOT>/dir/<SUBDIR>"
      ROOT: "/base"
      SUBDIR: "<YEAR>/<MONTH>"
      YEAR: "2023"
      MONTH: "October"
    files:
      - name: "file1"
        path: "<PATH>/file1.txt"
      - name: "file2"
        path: "<PATH>/file2.txt"
    """


def test_partial_placeholder_resolution(raw_yaml, global_variables_file):
    """
    Test partial resolution where variables depend on multi-stage substitution.
    """
    yaml_dict = {
        "variables": {
            "SUBDIR": "2023/October"
        }
    }
    resolved_yaml = parse_variables(
        raw_yaml, yaml_dict, global_variables_file, gui_mode=False, confirm=False
    )
    expected_yaml = """
    variables:
      PATH: "/base/dir/2023/October"
      ROOT: "/base"
      SUBDIR: "2023/October"
      YEAR: "2023"
      MONTH: "October"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_mixed_local_global_resolution(raw_yaml, global_variables_file):
    """
    Test proper precedence and merging of local and global variables, ensuring
    that a local override for ROOT is used in expansions but the raw definition
    for ROOT remains in the final output if it has no placeholders.
    """
    # Here, we override ROOT to expand to <BASEPATH>/local_project
    # which yields /local_path/local_project during expansions.
    yaml_dict = {
        "variables": {
            "BASEPATH": "/local_path",
            "ROOT": "<BASEPATH>/local_project",  # <--- override for expansions
        }
    }
    resolved_yaml = parse_variables(
        raw_yaml, yaml_dict, global_variables_file, gui_mode=False, confirm=False
    )
    # We expect that "<ROOT>" in PATH picks up the local override => /local_path/local_project
    # while the line "ROOT: '/base'" in raw YAML remains unchanged in final text (since it has no placeholders).
    expected_yaml = """
    variables:
      PATH: "/local_path/local_project/dir/2023/October"
      ROOT: "/base"
      SUBDIR: "2023/October"
      YEAR: "2023"
      MONTH: "October"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_placeholders_in_global_variables():
    """
    Test resolution of placeholders defined in the global variables file.
    """
    raw_yaml = """
    variables:
      FINALPATH: "<PATH>/final"
    """
    global_vars = """
    ROOT: "/base"
    PATH: "<ROOT>/project"
    """
    with patch("builtins.open", mock_open(read_data=global_vars)):
        resolved_yaml = parse_variables(
            raw_yaml, {}, "mock_global_variables.yaml", gui_mode=False, confirm=False
        )
        expected_yaml = """
        variables:
          FINALPATH: "/base/project/final"
        """
        assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_unresolved_variables_left(raw_yaml_unresolved, global_variables_file):
    """
    Ensure unresolved variables raise errors if not supplied by local/global.
    SUBDIR is missing in raw_yaml_unresolved, so if local/global doesn't
    define it, it's truly unresolved.
    """
    yaml_dict = {
        "variables": {
            "YEAR": "2023"
            # NO SUBDIR HERE
        }
    }
    with pytest.raises(ValueError, match="Unresolved placeholders found: SUBDIR"):
        parse_variables(
            raw_yaml_unresolved, yaml_dict, global_variables_file, gui_mode=False, confirm=False
        )


def test_empty_input(global_variables_file):
    """
    Test handling of an empty YAML input.
    """
    resolved_yaml = parse_variables("", {}, global_variables_file, gui_mode=False, confirm=False)
    assert yaml.safe_load(resolved_yaml) == {}


def test_invalid_placeholder_syntax():
    """
    Test handling of invalid placeholder syntax.
    """
    raw_yaml = """
    variables:
      A: "<VAR"
    """
    global_variables_file = "dummy_file.yaml"  # Placeholder, as no globals are needed
    with pytest.raises(ValueError, match="Invalid placeholder syntax in: <VAR"):
        parse_variables(raw_yaml, {}, global_variables_file, gui_mode=False, confirm=False)


def test_large_and_complex_yaml(large_yaml, global_variables_file):
    """
    Test resolution of a large and complex YAML with nested placeholders.
    """
    resolved_yaml = parse_variables(large_yaml, {}, global_variables_file, gui_mode=False, confirm=False)
    expected_yaml = """
    variables:
      PATH: "/base/dir/2023/October"
      ROOT: "/base"
      SUBDIR: "2023/October"
      YEAR: "2023"
      MONTH: "October"
    files:
      - name: "file1"
        path: "/base/dir/2023/October/file1.txt"
      - name: "file2"
        path: "/base/dir/2023/October/file2.txt"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_gui_mode_no_confirmation(tmp_path):
    raw_yaml = """
    variables:
      PATH: "<ROOT>/default_path"
    """
    global_variables_file = tmp_path / "global_variables.yaml"
    global_variables_file.write_text("ROOT: /base")
    resolved_yaml = parse_variables(raw_yaml, {}, str(global_variables_file), gui_mode=True, confirm=True)
    expected_yaml = """
    variables:
      PATH: "/base/default_path"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_non_gui_mode_with_confirmation(monkeypatch, tmp_path):
    raw_yaml = """
    variables:
      PATH: "<ROOT>/default_path"
    """
    global_variables_file = tmp_path / "global_variables.yaml"
    global_variables_file.write_text("ROOT: /base")

    # Mock user input to confirm the changes
    monkeypatch.setattr("builtins.input", lambda _: "yes")
    resolved_yaml = parse_variables(raw_yaml, {}, str(global_variables_file), gui_mode=False, confirm=True)
    expected_yaml = """
    variables:
      PATH: "/base/default_path"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_non_gui_mode_with_rejection(monkeypatch, tmp_path):
    raw_yaml = """
    variables:
      PATH: "<ROOT>/default_path"
    """
    global_variables_file = tmp_path / "global_variables.yaml"
    global_variables_file.write_text("ROOT: /base")

    # Mock user input to reject the changes
    monkeypatch.setattr("builtins.input", lambda _: "no")
    with pytest.raises(ValueError, match="User did not confirm the resolved YAML."):
        parse_variables(raw_yaml, {}, str(global_variables_file), gui_mode=False, confirm=True)


def test_optional_vars_with_gui_mode(tmp_path):
    raw_yaml = """
    variables:
      PATH: "<ROOT>/default_path"
    """
    optional_vars = {"ROOT": "/optional"}
    global_variables_file = tmp_path / "global_variables.yaml"
    global_variables_file.write_text("ROOT: /base")
    resolved_yaml = parse_variables(raw_yaml, {}, str(global_variables_file), gui_mode=True, optional_vars=optional_vars)
    expected_yaml = """
    variables:
      PATH: "/optional/default_path"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_empty_optional_vars_with_gui_mode(tmp_path):
    raw_yaml = """
    variables:
      PATH: "<ROOT>/default_path"
    """
    global_variables_file = tmp_path / "global_variables.yaml"
    global_variables_file.write_text("ROOT: /base")
    resolved_yaml = parse_variables(raw_yaml, {}, str(global_variables_file), gui_mode=True, optional_vars={})
    expected_yaml = """
    variables:
      PATH: "/base/default_path"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)


def test_mixed_sources_resolution(tmp_path):
    raw_yaml = """
    variables:
      FINAL_PATH: "<OPTIONAL_ROOT>/<LOCAL_DIR>/<GLOBAL_FILE>"
    """
    yaml_dict = {"variables": {"LOCAL_DIR": "local_dir"}}
    global_variables_file = tmp_path / "global_variables.yaml"
    global_variables_file.write_text("GLOBAL_FILE: file.txt")
    optional_vars = {"OPTIONAL_ROOT": "/optional"}
    resolved_yaml = parse_variables(
        raw_yaml,
        yaml_dict,
        str(global_variables_file),
        gui_mode=False,
        confirm=False,
        optional_vars=optional_vars
    )
    expected_yaml = """
    variables:
      FINAL_PATH: "/optional/local_dir/file.txt"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)