import os
import yaml
from enum import Enum

class ConfigKeys(Enum):
    APPS_DIRECTORY = "apps_directory"
    TEMPLATES_DIRECTORY = "templates_directory"
    ZONE_CONFIGS_DIRECTORY = "zone_configs_directory"
    SCRIPTS_DIRECTORY = "scripts_directory"
    DEFAULT_TEXT_EDITOR = "default_text_editor"
    GLOBAL_CONFIGS_DIRECTORY = "global_configs_directory"


class Config:
    """ Global configuration for desktop_compose """

    def __init__(self, config_file=None):
        self.config_file = config_file or os.path.expanduser("~/.config/desktop_compose/config.yaml")

        # Default values
        self.apps_directory = os.path.expanduser("~/.config/desktop_compose/apps")
        self.templates_directory = os.path.expanduser("~/.config/desktop_compose/templates")
        self.zone_configs_directory = os.path.expanduser("~/.config/desktop_compose/zone_configs")
        self.scripts_directory = os.path.expanduser("~/.config/desktop_compose/scripts")
        self.global_variables_file = os.path.expanduser("~/.config/desktop_compose/variables.yaml")
        self.default_text_editor = "code"

        self.initialize_config()

    def initialize_config(self):
        """Initialize the configuration by loading or creating defaults."""
        if not os.path.exists(self.config_file):
            self.create_default_config()
        else:
            try:
                self.load_config()
            except yaml.YAMLError as e:
                self.handle_yaml_error(e)

        # Ensure all directories exist
        self.ensure_directories()

    def create_default_config(self):
        """Create a default configuration file with default paths."""
        self.ensure_directories()
        config_data = {
            ConfigKeys.APPS_DIRECTORY.value: self.apps_directory,
            ConfigKeys.TEMPLATES_DIRECTORY.value: self.templates_directory,
            ConfigKeys.ZONE_CONFIGS_DIRECTORY.value: self.zone_configs_directory,
            ConfigKeys.SCRIPTS_DIRECTORY.value: self.scripts_directory,
            ConfigKeys.DEFAULT_TEXT_EDITOR.value: self.default_text_editor,
            ConfigKeys.GLOBAL_CONFIGS_DIRECTORY.value: self.global_variables_file,
        }
        self.write_yaml(self.config_file, config_data)

    def load_config(self):
        """Load configuration from the YAML file."""
        with open(self.config_file, "r") as f:
            config_data = yaml.safe_load(f) or {}

        # Update from config file if keys exist
        if ConfigKeys.APPS_DIRECTORY.value in config_data:
            self.apps_directory = config_data[ConfigKeys.APPS_DIRECTORY.value]
        if ConfigKeys.TEMPLATES_DIRECTORY.value in config_data:
            self.templates_directory = config_data[ConfigKeys.TEMPLATES_DIRECTORY.value]
        if ConfigKeys.ZONE_CONFIGS_DIRECTORY.value in config_data:
            self.zone_configs_directory = config_data[ConfigKeys.ZONE_CONFIGS_DIRECTORY.value]
        if ConfigKeys.DEFAULT_TEXT_EDITOR.value in config_data:
            self.default_text_editor = config_data[ConfigKeys.DEFAULT_TEXT_EDITOR.value]
        if ConfigKeys.GLOBAL_CONFIGS_DIRECTORY.value in config_data:
            self.global_variables_file = config_data[ConfigKeys.GLOBAL_CONFIGS_DIRECTORY.value]

    def handle_yaml_error(self, error):
        """Handle YAML errors by printing line number and exiting."""
        line_number = self.get_error_line_number(error)
        print(f"Error in config at line {line_number}. To correct, run with `--create_default_config`.")
        exit(1)

    def get_error_line_number(self, error):
        """Get the line number from a YAML error if available."""
        return getattr(error, "problem_mark", None).line + 1 if hasattr(error, 'problem_mark') else "unknown"

    def ensure_directories(self):
        """Ensure that all directories exist."""
        directories = [
            self.apps_directory,
            self.templates_directory,
            self.zone_configs_directory,
            self.scripts_directory,
        ]
        for path in directories:
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def write_yaml(filename, data):
        """Write data to a YAML file."""
        with open(filename, "w") as f:
            yaml.dump(data, f
                      )
