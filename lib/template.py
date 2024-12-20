import os.path
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
    def __init__(self,
                 name: str,
                 description: str,
                 apps: Optional[List[dict]] = None,
                 zone_file: Optional[str] = None):
        # Initialize basic attributes
        self.name = name
        self.description = description
        # Load apps using the helper function; pass an empty list if apps is None
        self.apps: List[App] = load_apps(apps or [])
        # Parse the zone configuration if a zone file is provided
        self.parse_zone_configs(zone_file)

    def launch(self):
        pyvda.VirtualDesktop.create().go()
        for app in self.apps:
            app.open()

    def parse_zone_configs(self, zone_file: Optional[str]):
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
        with open(f"{config.templates_directory}/{template_name}.yaml") as f:
            return Templates(**yaml.safe_load(f))
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
