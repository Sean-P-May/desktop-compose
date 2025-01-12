import os
import subprocess
from typing import List, Optional
import pyvda
import yaml
import logging

from lib.app import App, LocalAppConfig, AppConfig
from lib.config import Config
from lib.position import Position
from lib.layout import Monitor, Layout
from lib.templates.run_scripts import resolve_and_execute

logger = logging.getLogger(__name__)
config = Config()


class Template:
    name: str
    file_name: str
    parent_directory: str
    description: str
    layouts: list[Layout]
    after_scripts: Optional[List[str]] = None,
    before_scripts: Optional[List[str]] = None,
    apps: List[App]

    def __init__(self,
                 name: Optional[str] = "",
                 file_path: Optional[str] = "",
                 description: Optional[str] = "",
                 apps: Optional[List[dict]] = None,
                 after_scripts: Optional[List[str]] = None,
                 before_scripts: Optional[List[str]] = None,
                 layout: Optional[List[dict]] = None,
                 ):
        self.name = name
        self.parent_directory = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)
        self.description = description

        self.apps: List[App] = load_apps(apps or [])

        # Default to an empty list if layout is None
        self.layouts = [Layout(**layout) for layout in (layout or [])]

        self.before_scripts = before_scripts
        self.after_scripts = after_scripts
        self.parse_layout()


    def parse_layout(self):
        monitors = []
        for monitor_number, layout in enumerate(self.layouts):
            print(layout)
            monitors.append(Monitor(monitor_number - 1, layout))

        print(monitors)

        for app in self.apps:
            print("whore", app.local_config.monitor - 1)
            app.position = monitors[app.local_config.monitor - 1].resolve_position(app.local_config.location)



    def launch(self):
        desktop = pyvda.VirtualDesktop.create()
        desktop.rename(self.name)
        desktop.go()
        if self.before_scripts:
            for script in self.before_scripts:
                resolve_and_execute(script)

        for app in self.apps:
            app.launch()

        if self.after_scripts:
            for script in self.after_scripts:
                resolve_and_execute(script)

    def edit(self):
        subprocess.run([config.default_text_editor, self.parent_directory])

    def save(self):
        with open(os.path.join(self.parent_directory, self.file_name), "w") as f:
            f.write(
                yaml.dump(
                    self.__dict__(),
                    default_flow_style=False,
                    sort_keys=False, )
            )



    def __dict__(self):
        """Convert the template to a dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "layout": [layout.__dict__ for layout in self.layouts],  # Convert Layout objects to dict
            "before_scripts": self.before_scripts,
            "after_scripts": self.after_scripts,
            "apps": [app.local_config.__dict__ for app in self.apps],
        }





def load_apps(apps_yaml: List[dict]) -> List[App]:
    """
    Load applications based on their YAML configurations.
    Returns a list of App objects.
    """
    loaded_apps = []
    for app_data in apps_yaml:
        logger.info(f"Loading app data: {app_data}")
        print(app_data)
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


