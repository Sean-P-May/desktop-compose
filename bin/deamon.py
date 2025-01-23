import subprocess
import time

import keyboard
import pyvda
import win32con
import win32gui


def close_virtual_desktop():
    desktop = pyvda.VirtualDesktop.current()
    for app in desktop.apps_by_z_order():
        hwnd = app.hwnd
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception as e:
            print(f"Failed to close window: {e}")
            return


    desktops = pyvda.get_virtual_desktops()
    for desktop in desktops:
        print(f"Desktop: {desktop.name}")
    for i, desktop_ in enumerate(desktops):
         if desktop is desktop_:
             try:
                desktops[i-1].go()
             except  IndexError:
                print(f"not enough desktops")



    desktop.remove()

def open_gui_desktop():
    subprocess.run(r"C:\Users\smay1\OneDrive\CSC2212\Classwork\desktop_compose_ui\build\windows\x64\runner\Release\desktop_compose_ui.exe")


def new_desktop():
    desktop = pyvda.VirtualDesktop.create().go()

def create_desktop():
    desktop = pyvda.VirtualDesktop.create()

keyboard.add_hotkey('windows+esc', close_virtual_desktop)
keyboard.add_hotkey('windows+c', open_gui_desktop)
keyboard.add_hotkey('windows+enter', new_desktop)
keyboard.wait()
