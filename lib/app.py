import os
import time
from dataclasses import dataclass, field
from typing import Optional, List
from ctypes import cast, c_wchar_p
import subprocess

import pyvda
import win32con
import win32gui
import yaml
from pyvda import VirtualDesktop

from lib.config import Config
from lib.position import Position
from lib.layout import Location



@dataclass
class AppConfig:
    """
    Global configuration for an app.

    Attributes:
        path (str): The path to the application executable.
        default_position (Optional[Position]): The default position of the application window.
        default_args (List[str]): The default arguments to pass to the application.
        kill_before_start_command (Optional[str]): Command to kill the application before starting it.
        state (Optional[bool]): The state of the application.
    """
    path: str
    default_position: Optional[Position] = field(default_factory=lambda: Position())
    default_args: List[str] = field(default_factory=list)
    move_if_opened: Optional[bool] = False
    state: Optional[bool] = False
    delay: Optional[float] = 0.0


class LocalAppConfig:
    """
    Local configuration overrides for an app.

    Attributes:
        app (str): The name of the application.
        args (List[str]): The arguments to pass to the application.
        zone (Optional[str]): The zone configuration for the application.
        minimize (Optional[bool]): Whether to minimize the application on start.
        position (Optional[Position]): The position of the application window.
    """
    app: str
    args: List[str] = field(default_factory=list)
    monitor: int = 0
    location: Optional[Location] = None
    minimize: Optional[bool] = False




    def __init__(self, app: str,
                 monitor: int,
                 args: Optional[List[str]] = [],
                 location: Optional[dict] = None,
                 minimize: Optional[bool] = False):

        self.app = app
        self.args = args
        self.monitor = monitor - 1
        self.location = Location(**location) if location else None
        self.minimize = minimize

    def __dict__(self):
        return {
            "app": self.app,
            "args": self.args,
            "monitor": self.monitor + 1,
            "location": (self.location.__dict__() if self.location else None),
            "minimize": self.minimize,
        }










class App:
    """
    Combines global (AppConfig) and local (LocalAppConfig) configurations.

    Methods:
        open(): Launch the app and store its window handle.
        move_window(force: bool = False): Move the application window to the specified position.
        get_window_position() -> Position: Get the current position of the application window.
        resolve_path(): Resolve the path to the application executable.
        resolve_args(): Resolve the arguments to pass to the application.
        resolve_position(): Resolve the position of the application window.
        resolve_minimize(): Resolve whether to minimize the application on start.
        resolve_kill_command(): Resolve the command to kill the application before starting it.
    """

    def __init__(self, app_config: AppConfig, local_config: LocalAppConfig, zone_config_file: Optional[str] = None):
        """
        Initialize the App with global and local configurations.

        Args:
            app_config (AppConfig): The global configuration for the app.
            local_config (LocalAppConfig): The local configuration overrides for the app.
            zone_config_file (Optional[str]): The zone configuration file.
        """
        self.app_config = app_config
        self.local_config = local_config
        self.window_handle = None
        self.process = None
        self.position = None

    def launch(self):
        """
        Launch the app and store its window handle.
        """
        handles_already_added = []
        print(f"Launching App: {self.local_config.app}")
        if self.app_config.move_if_opened:
            print("checking if the app is opened")
            desktops = pyvda.get_virtual_desktops()
            for desktop in desktops:
                for app in  desktop.apps_by_z_order():
                    try:
                        app_id = cast(app.app_id, c_wchar_p).value  # Safely dereference
                    except AttributeError:
                        app_id = None
                    if isinstance(app_id, str):
                        if self.local_config.app.lower() in app_id.lower():
                            self.window_handle = app.hwnd
                            handles_already_added.append(self.window_handle)
                            app.move(VirtualDesktop.current())





        else:
            self.process = subprocess.Popen([self.resolve_path()] + self.resolve_args(), shell=True,
                                            creationflags=subprocess.DETACHED_PROCESS)
            time.sleep(self.app_config.delay)
            self.window_handle = _get_window_handle()

        self.move_window()

    def move_window(self, retries: int = 0):
        print(self.window_handle)
        if not self.window_handle:
            print("Invalid window handle. Skipping move.")
            return

        position = self.resolve_position()
        window_handle = self.window_handle

        offset = Position(
            x=-7,
            y=-3,
            width=14,
        )

        position = position + offset
        x, y, width, height = position

        try:
            win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
            win32gui.MoveWindow(window_handle, x, y, width, height, True)
            if self.get_window_position() != position and retries < 5:
                self.move_window(retries + 1)
        except Exception as e:
            print(f"Failed to move window: {e}")

    def get_window_position(self) -> Position:
        """
        Get the current position of the application window.

        Returns:
            Position: The current position of the application window.
        """
        if not self.window_handle:
            return Position(0, 0, 0, 0)
        rect = win32gui.GetWindowRect(self.window_handle)
        x = rect[0]
        y = rect[1]
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        return Position(x, y, width, height)

    def resolve_path(self):
        """
        Resolve the path to the application executable.

        Returns:
            str: The path to the application executable.
        """
        return self.app_config.path

    def resolve_args(self):
        """
        Resolve the arguments to pass to the application.

        Returns:
            List[str]: The arguments to pass to the application.
        """
        if not self.local_config.args and not self.app_config.default_args:
            return []
        elif not self.local_config.args:
            return self.app_config.default_args
        elif not self.app_config.default_args:
            return self.local_config.args
        else:
            return self.app_config.default_args + self.local_config.args

    def resolve_position(self):
        """
        Resolve the position of the application window.

        Returns:
            Position: The position of the application window.
        """
        return self.position or self.app_config.default_position

    def resolve_minimize(self):
        """
        Resolve whether to minimize the application on start.

        Returns:
            bool: Whether to minimize the application on start.
        """
        return self.local_config.minimize if self.local_config.minimize is not None else False

    def __dict__(self):
        return self.local_config.__dict__()





def _get_window_handle(previous_window_handles=[], retries=1500):
    """
    Get the window handle of the application.


    Args:
        previous_window_handles (List[int]): The list of previous window handles.
        retries (int): The number of retries to get the window handle.

    Returns:
        int: The window handle of the application.

    Raises:
        RuntimeError: If the window handle could not be found after the specified retries.
    """
    if retries == 0:  # prevent forever loop
        print("try increasing retries")
        raise RuntimeError

    current_window_handles = (
            [app.hwnd for app in pyvda.VirtualDesktop.current().apps_by_z_order()]
            + previous_window_handles)

    # Find a window_handle that is not in the previous_window_handles
    for window_handle in current_window_handles:
        if window_handle not in previous_window_handles:
            previous_window_handles.append(window_handle)
            return window_handle

    #Recursion is necessary to prevent the wrong window handel being assigned
    # Retry with reduced attempts
    return _get_window_handle(previous_window_handles, retries - 1)


def list_all_apps() -> None:
    config = Config()
    for app_file in os.listdir(config.apps_directory):
        with open(os.path.join(config.apps_directory, app_file)) as file:
            yaml_text = file.read()
            app_name = app_file.split(".")[0]
            app_config = AppConfig(**yaml.safe_load(yaml_text))
            print(f"{'-' * 60}\n{app_name}\npath:   {app_config.path}\ndefault_args:   {app_config.default_args}")


