import os
import yaml
from dataclasses import dataclass, field


@dataclass
class Config:
    """ Global configuration for desktop_compose """
    _config_file: str = field(default=os.path.expanduser("~/.config/desktop_compose/config.yaml"))
    apps_directory: str = field(default=os.path.expanduser("~/.config/desktop_compose/apps"))
    templates_directory: str = field(default=os.path.expanduser("~/.config/desktop_compose/templates"))
    zone_configs_directory: str = field(default=os.path.expanduser("~/.config/desktop_compose/zone_configs"))
    default_text_editor: str = field(default="code")



    _instance = None

    def __new__(cls, *args, **kwargs):
        """ Singleton pattern """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __post_init__(self):
        self.load_or_create_config()

    def load_or_create_config(self):
        if not os.path.exists(self._config_file):
            self.create_default_config()
        else:
            try:
                self.load_config()
            except yaml.YAMLError as e:
                line_number = self.get_error_line_number(e)
                print(f"Error in config at line {line_number}. To correct, run with `--create_default_config`.")
                exit(1)


        paths = [self.apps_directory, self.templates_directory, self.zone_configs_directory]

        # Ensure all directories exist
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

    def create_default_config(self):
        paths = [
            os.path.expanduser("~/.config/desktop_compose/apps"),
            os.path.expanduser("~/.config/desktop_compose/templates"),
            os.path.expanduser("~/.config/desktop_compose/zone_configs")
        ]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

        with open(self._config_file, "w") as f:
            yaml.dump({
                "apps_directory": self.apps_directory,
                "templates_directory": self.templates_directory,
                "zone_configs_directory": self.zone_configs_directory,
                "default_text_editor": self.default_text_editor,
            }, f)



    def load_config(self):
        with open(self._config_file, "r") as f:
            config_file = yaml.safe_load(f)
            self.apps_directory = config_file["apps_directory"]
            self.templates_directory = config_file["templates_directory"]
            self.zone_configs_directory = config_file["zone_configs_directory"]
            self.default_text_editor = config_file["default_text_editor"]

    def get_error_line_number(self, error):
        if hasattr(error, 'problem_mark'):
            return error.problem_mark.line + 1
        return "unknown"