from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Position:
    ''' Represents the position and size of a window '''
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __add__(self, other: 'Position') -> 'Position':
        return Position(
            self.x + other.x,
            self.y + other.y,
            self.width + other.width,
            self.height + other.height)

    def __sub__(self, other:  'Position') -> 'Position':
        return Position(
            self.x - other.x,
            self.y - other.y,
            self.width - other.width,
            self.height - other.height)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.width
        yield self.height
