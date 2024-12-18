import os
import sys
import time
from pprint import pprint

import pyvda

import yaml

from lib.app import AppConfig, App, LocalAppConfig
from lib.config import Config
from lib.template import Templates


def load_template(template_name: str, config: Config):
    if os.path.exists(f"{config.templates_directory}/{template_name}.yaml"):
        with open(f"{config.templates_directory}/{template_name}.yaml") as f:
            return Templates(**yaml.safe_load(f))
    else:
        print(f"Template not found: {template_name}")


def main(input_path):
    config = Config()
    template = load_template(input_path, config)
    desktop = pyvda.VirtualDesktop.create()
    desktop.go()

    for app in template.apps:
        app.open()

    # for app in template.apps:
    #     app.move_window()

    for app in template.apps:
        print(f"debug app: {app.local_config.app}: {app.window_handle}: {app.get_window_position()}: {app.resolve_position()}")



if __name__ == '__main__':
    input_path = sys.argv[1]
    main(input_path)
