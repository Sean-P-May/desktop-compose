import sys
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Commands(Enum):
    LIST = "--list"
    APPS = "--apps"
    RESET_CONFIG = "--reset_config"
    LIST_LAYOUTS = "--list-layouts"
    CREATE_TEMPLATE = "--create_template"
    CREATE_APP_CONFIG = "--create_app_config"
    CREATE_LAYOUT = "--create_layout"
    VERBOSE = "--verbose"
    LOG = "--log"
    ALTERNATE_CONFIG = "--alternate-config"
    HELP = "--help"
    SHORT_HELP = "-h"
    SHORT_EDIT = "-e"
    EDIT = "--edit"

alias_mapping = {
    "-l": Commands.LIST.value,
    "-a": Commands.APPS.value,
    "-r": Commands.RESET_CONFIG.value,
    "-h": Commands.HELP.value,
    "-e": Commands.EDIT.value,
    # Note: We are NOT adding --l here to keep this minimal and test just the basic logic.
}

def normalize_command(arg):
    return alias_mapping.get(arg, arg)

@dataclass
class ParsedArguments:
    standalone: Optional[Commands] = None
    creation_command: Optional[Commands] = None
    creation_name: Optional[str] = None
    verbose: bool = False
    log: bool = False
    edit: bool = False
    alternate_config: Optional[str] = None
    template: Optional[str] = None

def print_help():
    print(
        """
        Desktop-Compose: A powerful tool for managing virtual desktops and automating desktop application layouts and workflows.
    
        It uses YAML configurations to define how applications are arranged, launched, and managed across monitors and virtual desktops.
    
        Usage:
          desktop-compose [runtime options] [standalone command | creation command | template]
    
        Options:
    
          Standalone Commands:
            -l, --list              List all Templates
            -a, --apps              List all Application Configurations
            -r, --reset_config      Reset the configuration to defaults
            -h, --help              Show this help message and exit
            --list-layouts          List all Layouts
    
          Creation Commands:
            Use these commands to create new configuration files. The default text editor is defined in `~/.config/desktop_compose/config.yaml`:
    
            --create_template [template_name]     Create a new Template with the given name
            --create_app_config [app_name]        Create a new Application configuration file with the given name
            --create_layout [layout_name]         Create a new Layout file with the given name
    
          Runtime Options:
            These options can be combined with **Standalone Commands**, **Creation Commands**, or **Template Usage**:
    
            -v, --verbose          Show verbose output
            --log                  Log verbose output
            --alternate-config [path_to_config]  Use an alternate configuration file
        """
    )

def parse_arguments(args: []) -> Optional[ParsedArguments]:
    # Debugging
    print(f"DEBUG: Initial args = {args}")

    if not args or Commands.HELP.value in args or Commands.SHORT_HELP.value in args:
        print_help()
        return None

    parsed_args = ParsedArguments()

    standalone_flags = {Commands.LIST, Commands.APPS, Commands.RESET_CONFIG, Commands.LIST_LAYOUTS}
    creation_flags = {Commands.CREATE_TEMPLATE, Commands.CREATE_APP_CONFIG, Commands.CREATE_LAYOUT}
    runtime_flags = {Commands.VERBOSE, Commands.LOG, Commands.ALTERNATE_CONFIG, Commands.EDIT}

    i = 0
    while i < len(args):
        arg = normalize_command(args[i])
        print(f"DEBUG: Processing arg={arg}")

        if arg in [c.value for c in standalone_flags]:
            cmd = Commands(arg)
            print(f"DEBUG: Detected standalone command: {cmd}")
            if parsed_args.standalone:
                print(f"Error: Multiple standalone commands are not allowed: {arg} conflicts with {parsed_args.standalone.value}")
                sys.exit(1)
            parsed_args.standalone = cmd

        elif arg in [c.value for c in creation_flags]:
            cmd = Commands(arg)
            print(f"DEBUG: Detected creation command: {cmd}")
            if i + 1 >= len(args) or args[i + 1].startswith("-"):
                print(f"Error: Missing name for {arg}")
                sys.exit(1)
            parsed_args.creation_command = cmd
            parsed_args.creation_name = args[i + 1]
            i += 1

        elif arg in [c.value for c in runtime_flags]:
            print(f"DEBUG: Detected runtime flag: {arg}")
            if arg == Commands.ALTERNATE_CONFIG.value:
                if i + 1 >= len(args) or args[i + 1].startswith("-"):
                    print("Error: Missing path for --alternate-config")
                    sys.exit(1)
                parsed_args.alternate_config = args[i + 1]
                i += 1
            elif arg == Commands.VERBOSE.value:
                parsed_args.verbose = True
            elif arg == Commands.LOG.value:
                parsed_args.log = True
            elif arg == Commands.EDIT.value:
                parsed_args.edit = True

        elif not arg.startswith("-"):
            print(f"DEBUG: Detected template: {arg}")

            if parsed_args.template:
                print(f"Error: Multiple templates specified: {arg} conflicts with {parsed_args.template}")
                sys.exit(1)
            parsed_args.template = arg

        else:
            print(f"Error: Unknown argument: {arg}")
            sys.exit(1)

        i += 1

    print(f"DEBUG: Parsed arguments so far: {parsed_args}")

    # Final Checks
    if parsed_args.standalone and (parsed_args.creation_command or parsed_args.template):
        print("Error: Standalone commands cannot be combined with creation commands or templates.")
        sys.exit(1)

    if parsed_args.creation_command and parsed_args.template:
        print("Error: Creation commands cannot be combined with templates.")
        sys.exit(1)

    return parsed_args


if __name__ == "__main__":
    arguments = parse_arguments(sys.argv[1:])
    if arguments:
        print("Parsed Arguments:", arguments)
