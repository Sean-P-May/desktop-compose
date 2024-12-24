import os.path
import subprocess
import re
from typing import List, Optional

import pyvda
import yaml
import logging

from lib.app import App, LocalAppConfig, AppConfig
from lib.config import Config
from lib.position import Position
from lib.layout import Monitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config()


import os
import subprocess

def run_scripts(input_string):
    """
    Executes scripts or commands based on the input string.

    The input string can specify a file, directory, or shell command, optionally with arguments.
    - If a file is provided, it executes the file using the appropriate interpreter based on its extension.
    - If a directory is provided, it processes only the file matching the input name, if it exists.
    - If no valid file or directory is found, the input is treated as a shell command.
    - Additional arguments in the input string are passed to the executed script.

    Args:
        input_string (str): A string specifying the file, directory, or command, optionally with arguments.
    """
    commands = {
        ".py": ["python"],
        ".ps1": ["powershell", "-File"],
        ".sh": ["bash"],
        ".js": ["node"]
    }

    # Split input into potential script and arguments
    parts = input_string.split()
    if not parts:
        print("No input provided.")
        return

    script_candidate = parts[0]  # First word might be the script or directory
    arguments = parts[1:]  # Everything else are potential arguments

    # Full path of the script or directory
    script_path = os.path.join(config.scripts_directory, script_candidate)

    if os.path.isdir(script_path):  # If it's a directory
        found_script = False
        for file in os.listdir(script_path):
            full_path = os.path.join(script_path, file)
            file_name, file_extension = os.path.splitext(file)

            # Match exact name and supported extension
            if file_name == script_candidate and file_extension in commands:
                subprocess.run(commands[file_extension] + [full_path] + arguments)
                found_script = True
                break  # Stop after finding the matching script

        if not found_script:
            print(f"No matching script found for '{script_candidate}' in directory '{script_path}'.")
    elif os.path.isfile(script_path):  # If it's a file
        file_extension = os.path.splitext(script_candidate)[1]
        if file_extension in commands:  # File has a recognized extension
            subprocess.run(commands[file_extension] + [script_path] + arguments)
        elif not file_extension:  # File has no extension
            for ext, cmd in commands.items():
                candidate_path = script_path + ext
                if os.path.isfile(candidate_path):
                    subprocess.run(cmd + [candidate_path] + arguments)
                    break
        else:
            print(f"Unsupported file extension: {file_extension}")
    else:
        # If it's not a file or directory, attempt to run as a command
        process_result = subprocess.run(input_string, shell=True)
        if process_result.returncode != 0:
            print("Invalid script file, directory, or command. Check your input.")
            print(process_result.stdout)



class Templates:
    """
    The Templates class manages the configuration and layout of applications across monitors and zones.

    Attributes:
        name (str): The name of the template.
        description (str): A brief description of the template.
        apps (List[App]): A list of applications configured within this template.

    Methods:
        parse_zone_configs(zone_file):
            Parses zone configurations and assigns positions to applications.
        load_monitor_layouts(zone_file, config):
            Loads monitor layouts from a YAML configuration file.
        load_apps(apps_yaml):
            Loads and initializes applications from their YAML configurations.
    """
    # Class-level attributes for type hints
    name: str
    description: str
    apps: List[App]
    scripts: List[str]
    def __init__(self,
                 name: str,
                 description: str,
                 apps: Optional[List[dict]] = None,
                 after_scripts: Optional[List[str]] = None,
                 before_scripts: Optional[List[str]] = None,
                 layout_file: Optional[str] = None):
        # Initialize basic attributes
        self.name = name
        self.description = description
        # Load apps using the helper function; pass an empty list if apps is None
        self.apps: List[App] = load_apps(apps or [])
        # Parse the zone configuration if a zone file is provided
        self.parse_layout_configs(layout_file)
        self.before_scripts = before_scripts
        self.after_scripts = after_scripts

    def launch(self):
        pyvda.VirtualDesktop.create().go()
        if self.before_scripts:

            for script in self.before_scripts:
                run_scripts(script)

        for app in self.apps:
            app.open()

        if self.after_scripts:
            for script in self.after_scripts:
                print(script)
                run_scripts(script)

    def parse_layout_configs(self, zone_file: Optional[str]):
        """
        Parse the zone configurations from the provided file and
        assign positions to apps based on the monitor and zone layout.
        """
        if not zone_file:
            # Exit early if no zone file is provided
            return

        config = Config()  # Load global configuration settings

        # Load monitor layouts from the zone file
        monitors = load_monitor_layouts(zone_file, config)


        # Assign each app to the corresponding monitor and zone
        for app in self.apps:
            logger.info(f"Configuring app: {app}")
            # Retrieve the monitor and zone indices from the app's configuration
            monitor, zone = app.local_config.zone
            monitor, zone = int(monitor), int(zone)
            print(monitors)
            print(monitor, zone)
            app.local_config.position = monitors[monitor].app_positions[zone]
            logger.info(f"App position set: {app}")


def load_monitor_layouts(zone_file: str, config: Config) -> List[Monitor]:
    """
    Load and process monitor layouts from a YAML zone configuration file.
    Returns a list of Monitor objects with their respective zone layouts.
    """
    monitors = []
    # Open the YAML file containing zone configurations
    with open(os.path.join(config.zone_configs_directory, zone_file)) as f:
        monitor_layout_yaml = yaml.safe_load(f)
        for index, monitor_yaml in enumerate(monitor_layout_yaml):
            monitor = Monitor(index)
            # Process each zone layout within the monitor
            print(
                monitor_yaml["zones"]
            )
            for layout in monitor_yaml["zones"]:
                logger.info(f"Processing zone layout: {layout}")
                # Add the zone position to the monitor's zone layouts
                monitor.app_positions.append(Position(**layout["position"]))
                monitor.shift_positions()
            monitors.append(monitor)
    logger.info(f"Loaded monitors: {monitors}")
    return monitors


def load_template(template_name: str):
    if os.path.exists(f"{config.templates_directory}/{template_name}.yaml"):
        with open(f"{config.templates_directory}/{template_name}.yaml") as file:
            yaml_string = file.read()
            template_dict = yaml.safe_load(yaml_string)
            return Templates(template_name, template_dict)
    else:
        print(f"Template not found: {template_name}")
        exit(1)


def list_templates():
    if os.path.exists(config.templates_directory):
        print(os.listdir(config.templates_directory))
        for template_yaml_file in os.listdir(config.templates_directory):
            yaml_name = template_yaml_file.split(".")[0]
            template = load_template(yaml_name)
            print(template.name)
            print("--------------------------------------------------")
            print(yaml_name+".yaml")
            print(template.description)


def load_apps(apps_yaml: List[dict]) -> List[App]:
    """
    Load applications based on their YAML configurations.
    Returns a list of App objects.
    """

    config = Config()  # Load global configuration settings
    loaded_apps = []
    for app_data in apps_yaml:
        logger.info(f"Loading app data: {app_data}")
        # Create a local configuration for the app
        local_app_config = LocalAppConfig(**app_data)
        # Determine the path to the app's main configuration file
        app_path = os.path.join(config.apps_directory, f"{local_app_config.app}.yaml")
        if os.path.exists(app_path):
            # Load the app's configuration if the file exists
            with open(app_path) as f:
                app_config = AppConfig(**yaml.safe_load(f))
                # Create the App object and add it to the list
                app = App(app_config=app_config, local_config=local_app_config)
                loaded_apps.append(app)
                logger.info(f"App loaded: {app}")
    return loaded_apps


def parse_variables(raw_yaml: str, yaml_dict: dict, global_variables_file: str) -> str:
    """
    Parse and substitute variables in raw_yaml, using:
      1) Template variables from raw_yaml itself
      2) Local variables from yaml_dict
      3) Global variables from global_variables_file
    Then normalize paths to avoid double slashes.
    """
    # -----------------
    # 1. Load Global Variables
    # -----------------
    with open(global_variables_file, "r", encoding="utf-8") as f:
        global_vars = yaml.safe_load(f) or {}

    # -----------------
    # 2. Parse the raw_yaml into a Python dict so we can get template-defined variables
    # -----------------
    parsed_yaml = yaml.safe_load(raw_yaml) or {}
    template_vars = parsed_yaml.get("variables", {})

    # -----------------
    # 3. Merge local variables from yaml_dict into template_vars
    # -----------------
    local_vars = yaml_dict.get("variables", {})
    merged_vars = {**template_vars, **local_vars}  # local overrides template

    # Dictionary for final resolved values
    resolved_dict = {}
    # Detect real circular references
    resolving_stack = set()

    # Regex to match placeholders like <SOMETHING>
    placeholder_pattern = re.compile(r"<(.*?)>")

    def resolve_value(expression: str) -> str:
        """Recursively resolve placeholders in an expression string."""
        placeholders = placeholder_pattern.findall(expression)
        for ph in placeholders:
            ph_value = resolve_variable(ph)
            expression = expression.replace(f"<{ph}>", ph_value)
        return expression

    def resolve_variable(var_name: str) -> str:
        """Compute the final value of a single variable."""
        # Already resolved?
        if var_name in resolved_dict:
            return resolved_dict[var_name]

        # Check for real circular reference
        if var_name in resolving_stack:
            raise ValueError(f"Circular reference detected for variable '{var_name}'.")
        resolving_stack.add(var_name)

        # Value from local/template or global?
        if var_name in merged_vars:
            base_value = merged_vars[var_name]
        elif var_name in global_vars:
            base_value = global_vars[var_name]
        else:
            base_value = input(f"Enter value for {var_name}: ")

        # Recursively substitute any placeholders in base_value
        final_value = resolve_value(str(base_value))

        # Mark as resolved
        resolving_stack.remove(var_name)
        resolved_dict[var_name] = final_value
        return final_value

    # -----------------
    # 4. Resolve each variable in merged_vars
    # -----------------
    for key in merged_vars.keys():
        resolve_variable(key)

    # -----------------
    # 5. Substitute placeholders in raw_yaml
    # -----------------
    def substitute_placeholder(match):
        ph = match.group(1)
        return resolved_dict.get(ph, match.group(0))  # fallback: leave <ph> if unknown

    resolved_yaml = placeholder_pattern.sub(substitute_placeholder, raw_yaml)

    # -----------------
    # 6. Normalize double slashes in each resolved variable and in final YAML
    # -----------------
    def remove_double_slashes(path: str) -> str:
        """
        Replace multiple forward slashes '//' with a single slash '/',
        except if it appears after a colon (e.g. 'http://' should stay).
        This helps fix local file paths that might end up with //.
        """
        return re.sub(r'(?<!:)//+', '/', path)

    # Normalize each resolved dictionary entry
    for k, v in resolved_dict.items():
        resolved_dict[k] = remove_double_slashes(v)

    # Also normalize the final resolved YAML
    resolved_yaml = remove_double_slashes(resolved_yaml)

    return resolved_yaml

