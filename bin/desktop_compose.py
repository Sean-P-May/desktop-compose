import os
import sys

import pyvda

from lib.app import list_all_apps
from lib.config import Config
from lib.create_file import create_file
from lib.template import Templates, load_template, list_templates
from lib.phase_args import parse_arguments, ParsedArguments, Commands, print_help


def main() -> None :
    print(sys.argv[1:])
    args = parse_arguments(sys.argv[1:])


    if args.alternate_config is None:
        config = Config() #  need to add alternative config file logic
    else:
        config = Config()

    if args.standalone == Commands.LIST:
        list_templates()
        exit(0)

    if args.standalone == Commands.RESET_CONFIG:
        config.create_default_config()
        exit(0)


    if args.standalone == Commands.APPS:
        list_all_apps()
        exit(0)
    if args.creation_command:
        create_file(args)

    if args.template:
        template = load_template(args.template)
        template.launch()




    # for app in template.apps:
    #     print(f"debug app: {app.local_config.app}: {app.window_handle}: {app.get_window_position()}: {app.resolve_position()}")



if __name__ == '__main__':
    main()
