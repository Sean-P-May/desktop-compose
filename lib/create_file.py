import os
import subprocess
from shutil import copyfile
from lib.config import Config
from lib.phase_args import Commands, ParsedArguments

config = Config()

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the script directory
EXAMPLE_PATHS = {
    Commands.CREATE_TEMPLATE: os.path.join(script_directory, "../config_examples/templates/example_template.yaml"),
    Commands.CREATE_APP_CONFIG: os.path.join(script_directory, "../config_examples/apps/chrome.yaml"),
    Commands.CREATE_LAYOUT: os.path.join(script_directory, "../config_examples/apps/1x2.yaml")
}

# Define corresponding directory mappings
DIRECTORY_MAPPINGS = {
    Commands.CREATE_TEMPLATE: config.templates_directory,
    Commands.CREATE_APP_CONFIG: config.apps_directory,
    Commands.CREATE_LAYOUT: config.zone_configs_directory
}

def create_file(args: ParsedArguments):
    creation_file_name = f"{args.creation_name}.yaml"

    if args.creation_command not in EXAMPLE_PATHS:
        raise Exception("Unknown creation command")

    # Get the correct directory
    target_directory = DIRECTORY_MAPPINGS.get(args.creation_command)
    if not target_directory:
        raise AttributeError(f"No directory mapping found for {args.creation_command.name}")

    new_file_path = os.path.join(target_directory, creation_file_name)

    if os.path.exists(new_file_path) and args.edit:
        open_editor(new_file_path)
        return
    elif os.path.isfile(new_file_path):
        raise print(f"File '{new_file_path}' already exists.")

    copyfile(EXAMPLE_PATHS[args.creation_command], new_file_path)
    open_editor(new_file_path)


def open_editor(new_file_path: str):
    subprocess.Popen(
        [config.default_text_editor, new_file_path],
        shell=True,
        creationflags=subprocess.DETACHED_PROCESS
    )
