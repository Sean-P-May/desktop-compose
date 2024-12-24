import pytest
from lib.phase_args import parse_arguments, Commands, ParsedArguments  # Replace 'your_script_name' with the actual name of your script

def test_help_flag():
    args = ["--help"]
    assert parse_arguments(args) is None

def test_short_help_flag():
    args = ["-h"]
    assert parse_arguments(args) is None

def test_standalone_command():
    args = ["--list"]
    parsed = parse_arguments(args)
    assert parsed.standalone == Commands.LIST
    assert parsed.creation_command is None
    assert parsed.template is None

def test_creation_command_with_name():
    args = ["--create_template", "my_template"]
    parsed = parse_arguments(args)
    assert parsed.creation_command == Commands.CREATE_TEMPLATE
    assert parsed.creation_name == "my_template"

def test_verbose_flag():
    args = ["--verbose"]
    parsed = parse_arguments(args)
    assert parsed.verbose is True

def test_log_flag():
    args = ["--log"]
    parsed = parse_arguments(args)
    assert parsed.log is True

def test_alternate_config():
    args = ["--alternate-config", "/path/to/config.yaml"]
    parsed = parse_arguments(args)
    assert parsed.alternate_config == "/path/to/config.yaml"

def test_multiple_templates_error():
    args = ["template1", "template2"]
    with pytest.raises(SystemExit):
        parse_arguments(args)

def test_missing_creation_name():
    args = ["--create_template"]
    with pytest.raises(SystemExit):
        parse_arguments(args)

def test_standalone_and_creation_conflict():
    args = ["--list", "--create_template", "my_template"]
    with pytest.raises(SystemExit):
        parse_arguments(args)

def test_unknown_argument():
    args = ["--unknown"]
    with pytest.raises(SystemExit):
        parse_arguments(args)

def test_standalone_and_template_conflict():
    args = ["--list", "template"]
    with pytest.raises(SystemExit):
        parse_arguments(args)

def test_creation_command_and_template_conflict():
    args = ["--create_template", "my_template", "template"]
    with pytest.raises(SystemExit):
        parse_arguments(args)

def test_multiple_runtime_options():
    args = ["--verbose", "--log", "--alternate-config", "/path/to/config.yaml"]
    parsed = parse_arguments(args)
    assert parsed.verbose is True
    assert parsed.log is True
    assert parsed.alternate_config == "/path/to/config.yaml"

def test_template_usage():
    args = ["my_template"]
    parsed = parse_arguments(args)
    assert parsed.template == "my_template"
    assert parsed.standalone is None
    assert parsed.creation_command is None

def test_full_combination():
    args = ["--verbose", "my_template"]
    parsed = parse_arguments(args)
    assert parsed.verbose is True
    assert parsed.template == "my_template"
    assert parsed.standalone is None
    assert parsed.creation_command is None
