import os
import re
import sys
from typing import List
import yaml
from psutil import users

from lib.config import Config
from lib.templates.parse_variables import parse_variables
from lib.templates.template import Template

config = Config()


def save_template(template: Template, new_name: str, new_file_name: str) -> None:
    """
    Save a template with a new name and file path.

    Args:
        template (Template): The template object to save.
        new_name (str): The new name for the template.
        new_file_name (str): The new file path for the template (must end with .yaml).

    Raises:
        ValueError: If the new file name does not end with .yaml.
    """
    if not new_file_name.endswith(".yaml"):
        raise ValueError("new_file_name_or_path must end in .yaml")

    if os.path.exists(new_file_name):
        print("file_already_exists", new_file_name)
        print("not overwriting", new_file_name)
        return

    template.name = new_name
    template.file_name = new_file_name
    template.save()


def get_template_by_full_path(template_path: str) -> "Template":
    """
    Retrieve a template from a specified file path.

    Args:
        template_path (str): The full path to the template file.

    Returns:
        Template: The loaded template object.

    Raises:
        FileNotFoundError: If the template file does not exist.
        yaml.YAMLError: If the template file contains invalid YAML.
    """
    try:
        with open(template_path) as file:
            yaml_string = file.read()
            if "<" in yaml_string and ">" in yaml_string:
                template_dict = yaml.safe_load(yaml_string)
                template_dict = yaml.safe_load(
                    parse_variables(yaml_string, template_dict, config.global_variables_file))
                template = Template(**template_dict, file_path=template_path)

                users_input = input(
                    "If you would like to save, enter a new template name and file name or press enter to continue: ")
                if users_input.strip() == "":
                    return template

                users_input = users_input.split()
                if len(users_input) != 2:
                    print("Invalid input. Not saving resolved template.")
                    return template

                try:
                    save_template(template, users_input[0], users_input[1])
                    print("Template saved!")
                except ValueError as e:
                    print(e)
                    print("Not saving resolved template.")

                return template
            else:
                template_dict = yaml.safe_load(yaml_string)
                return Template(**template_dict, file_path=template_path)
    except FileNotFoundError:
        print(f"Could not find template file {template_path}.")
        sys.exit(1)

    except yaml.YAMLError as e:
        print("Invalid YAML file.")
        print(e)
        sys.exit(1)


def get_template_by_file_name(template_name: str):
    """
    Retrieve a template by its file name.

    Args:
        template_name (str): The name of the template file (must end with .yaml).

    Returns:
        Template: The loaded template object.
    """
    return get_template_by_full_path(
        os.path.join(config.templates_directory, template_name))


def get_all_templates() -> List[Template]:
    """
    Retrieve all templates in the templates directory.

    Returns:
        List[Template]: A list of loaded template objects.
    """
    templates = []
    for template_file in os.listdir(config.templates_directory):
        if template_file.endswith(".yaml"):
            templates.append(get_template_by_file_name(template_file))
    return templates


def get_template_by_name(template_name: str) -> Template:
    """
    Retrieve a template by its name.

    Args:
        template_name (str): The name of the template.

    Returns:
        Template: The matching template object, or None if not found.
    """
    templates = get_all_templates()
    for template in templates:
        if template.name == template_name:
            return template


def get_template(template_reference: str) -> Template:
    """
    Retrieve a template by its reference, which can be a file name, full path, or template name.

    Args:
        template_reference (str): The reference to the template.

    Returns:
        Template: The loaded template object.
    """
    if template_reference.endswith(".yaml") and os.path.isabs(template_reference):
        return get_template_by_full_path(template_reference)
    elif template_reference.endswith(".yaml"):
        return get_template_by_file_name(template_reference)
    else:
        return get_template_by_name(template_reference)


def list_templates():
    """
    List all templates in the templates directory and print them as YAML.

    Returns:
        None
    """
    templates = get_all_templates()
    templates_yaml_list = []

    for template in templates:
        dictionary = template.__dict__()
        templates_yaml_list.append(template.serialize_for_list())

    print(yaml.dump(templates_yaml_list, default_flow_style=False, sort_keys=False))
