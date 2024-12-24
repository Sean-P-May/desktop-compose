import pytest
import yaml
from lib.template import parse_variables

@pytest.fixture
def global_variables_file(tmp_path):
    """
    Fixture to create a temporary global variables file.
    Contains a single SUBJECTPATH variable as an example.
    """
    file_path = tmp_path / "global_variables.yaml"
    content = """
    SUBJECTPATH: ~/OneDrive/Schoolwork/english101/
    """
    file_path.write_text(content)
    return str(file_path)

@pytest.fixture
def raw_yaml():
    """
    Fixture for the template-like raw YAML containing placeholders.
    """
    return """
    variables:
      PATH: "<SUBJECTPATH>/papers/<PAPER>/"
      DOC: "<PATH>/<PAPER>_paper.docx"
    """

@pytest.fixture
def yaml_dict():
    """
    Fixture for local variables that partially fill placeholders.
    """
    return {
        "variables": {
            "PAPER": "History_Final"
        }
    }

def test_variable_resolution(raw_yaml, yaml_dict, global_variables_file):
    """
    Validate that <SUBJECTPATH> is taken from the global file,
    <PAPER> from the local yaml_dict, and that <PATH> is assembled
    and substituted correctly.
    """
    resolved_yaml = parse_variables(raw_yaml, yaml_dict, global_variables_file)
    expected_yaml = """
    variables:
      PATH: "~/OneDrive/Schoolwork/english101/papers/History_Final/"
      DOC: "~/OneDrive/Schoolwork/english101/papers/History_Final/History_Final_paper.docx"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)

def test_missing_variable_prompt(monkeypatch, raw_yaml, yaml_dict, global_variables_file):
    """
    Ensure the function prompts the user if a variable is not found
    in local or global vars, using monkeypatch to simulate user input.
    """
    # Remove PAPER from local vars to force user prompt
    del yaml_dict["variables"]["PAPER"]

    def mock_input(prompt):
        if "PAPER" in prompt:
            return "Research_Paper"
        return "Default_Value"  # fallback if needed

    monkeypatch.setattr("builtins.input", mock_input)
    resolved_yaml = parse_variables(raw_yaml, yaml_dict, global_variables_file)

    expected_yaml = """
    variables:
      PATH: "~/OneDrive/Schoolwork/english101/papers/Research_Paper/"
      DOC: "~/OneDrive/Schoolwork/english101/papers/Research_Paper/Research_Paper_paper.docx"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)

def test_recursive_resolution(raw_yaml, global_variables_file):
    """
    Validate that nested placeholders are correctly resolved,
    i.e., <COURSE> is replaced within <SUBJECTPATH>, which
    is then used in PATH and DOC.
    """
    yaml_dict = {
        "variables": {
            "PAPER": "Thesis",
            "SUBJECTPATH": "~/Documents/<COURSE>",
            "COURSE": "Advanced_Studies"
        }
    }
    resolved_yaml = parse_variables(raw_yaml, yaml_dict, global_variables_file)
    expected_yaml = """
    variables:
      PATH: "~/Documents/Advanced_Studies/papers/Thesis/"
      DOC: "~/Documents/Advanced_Studies/papers/Thesis/Thesis_paper.docx"
    """
    assert yaml.safe_load(resolved_yaml) == yaml.safe_load(expected_yaml)
