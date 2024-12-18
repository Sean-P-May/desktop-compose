from dataclasses import dataclass, field
from typing import List
from lib.position import Position


@dataclass
class ZoneLayout:
    zones: List[Position] = field(default_factory=list)


@dataclass
class Monitor:
    zone_layouts: List[ZoneLayout] = field(default_factory=list)



