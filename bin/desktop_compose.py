
from typing import Optional

import typer

from lib.app import list_all_apps
from lib.config import Config
from lib.templates.template_management import get_template, list_templates

app = typer.Typer(pretty_exceptions_enable=False)


# Global flags
verbose = False
log = False
config_path = None

@app.callback()
def main(

    verbose_flag: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    log_flag: bool = typer.Option(False, "--log", help="Log verbose output."),
    config: str = typer.Option(None, "--config", help="Use an alternate configuration file."),

):
    """
    Global options for Desktop-Compose.
    """
    global verbose, log, config_path
    verbose = verbose_flag
    log = log_flag
    config_path = config


    if config_path is None:
        config = Config()  # need to add alternative config file logic
    else:
        config = Config()


@app.command()
def launch(template: str = typer.Argument(..., help="Template to launch.  Either a template name template file or full path to a template"),):
    """ [template] launches the provided template creating new workspaces """
    template = get_template(template)
    template.launch()
    pass

@app.command()
def list(silent: bool = typer.Option(
    False,
    "--silent",
    "-s",
    help="list available templates without printing errors, useful for user interfaces "),):
    """lists all templates"""
    list_templates()


@app.command()
def apps(silent: bool = typer.Option(
    False,
    "--silent",
    "-s",
    help="list app configuration files without printing errors, useful for user interfaces "),):
    """lists all app configuration files"""
    list_all_apps()

@app.command()
def reset_config():
    """ Reset the configuration file to default values."""
    config = Config()
    config.create_default_config()

@app.command()
def create(name: str, file_name: Optional[str] = None):
    pass

@app.command()
def edit(template: str):
    template = get_template(template)
    template.edit()





@app.command()
def   duplicate(template: str, new_name: str, new_file_name: Optional[str] = typer.Argument("", help="defaults to [new_name}.yaml")):
    template = get_template(template)










@app.command()
def edit_app(name: str):
    pass
if __name__ == "__main__":
    app()