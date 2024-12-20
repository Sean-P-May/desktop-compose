from dataclasses import dataclass, field
from typing import List
import ctypes
from lib.position import Position
import screeninfo

# allows  this program To properly move windows with dbi
ctypes.windll.shcore.SetProcessDpiAwareness(2)

monitor_info_list= screeninfo.get_monitors()




class Monitor:
    app_positions: List[Position]
    monitor_info : screeninfo.Monitor

    def __init__(self, monitor_index: int):
        self.app_positions = []
        self.monitor_info = monitor_info_list[monitor_index]
        self.offset_position = Position(
            x =self.monitor_info.x,
            y= self.monitor_info.y,
        )

    def shift_positions(self):
        for index, position in enumerate(self.app_positions):
            self.app_positions[index] = position + self.offset_position

