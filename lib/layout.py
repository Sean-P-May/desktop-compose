import ctypes
from dataclasses import dataclass
from typing import Optional

from lib.position import Position
import screeninfo

# Set the process DPI awareness for proper scaling of windows on high-DPI displays
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# Get a list of monitor information, including dimensions and positions
monitor_info_list = screeninfo.get_monitors()


class Location:
    """
    Represents a window's location on a grid.

    Attributes:
        row (int): The grid row where the window starts.
        col (int): The grid column where the window starts.
        row_span (Optional[int]): Number of rows the window spans. Defaults to None.
        col_span (Optional[int]): Number of columns the window spans. Defaults to None.
    """
    row: int
    col: int
    row_span: Optional[int] = None
    col_span: Optional[int] = None

    def __init__(self, row: int, col: int, row_span: Optional[int] = None, col_span: Optional[int] = None):
        self.row = row
        self.col = col
        self.row_span = row_span
        self.col_span = col_span


    def __dict__(self):
        if self.row_span is None and self.col_span is None:
            return {
                "row": self.row,
                "col": self.col,
            }
        else:
            return {
                "row": self.row,
                "col": self.col,
                "row_span": self.row_span,
                "col_span": self.col_span,
            }




@dataclass
class Layout:
    """
    Defines a grid layout for a monitor.

    Attributes:
        rows (int): Total number of rows in the grid.
        cols (int): Total number of columns in the grid.
    """
    rows: int
    cols: int

    def __dict__(self):
        return {
            "rows": self.rows,
            "cols": self.cols,
        }


class Monitor:
    """
    Represents a monitor with grid-based layout capabilities.

    Attributes:
        cols (int): Number of columns in the grid.
        rows (int): Number of rows in the grid.
        monitor_info (screeninfo.Monitor): Information about the monitor.
    """

    def __init__(self, monitor_index: int, layout: Layout):
        """
        Initialize a Monitor object.

        Args:
            monitor_index (int): Index of the monitor in the monitor info list.
            layout (Layout): Grid layout specifying rows and columns.

        Raises:
            ValueError: If cols or rows in the layout are less than 1.
        """
        cols = layout.cols
        rows = layout.rows
        if cols < 1 or rows < 1:
            raise ValueError("cols and rows must be positive")
        self.cols = cols
        self.rows = rows
        self.monitor_info = monitor_info_list[monitor_index]

    def resolve_position(self, location: Location) -> Position:
        """
        Resolve the pixel-based position of a grid cell or area.

        Args:
            location (Location): Location on the grid to resolve.

        Returns:
            Position: The pixel-based position of the specified location.

        If no location is provided, returns the monitor's full-screen position.
        """
        if location is None:
            return Position(
                x=self.monitor_info.x,
                y=self.monitor_info.y,
                width=self.monitor_info.width,
                height=self.monitor_info.height,
            )

        row, col = location.row, location.col
        row_span, col_span = location.row_span or 1, location.col_span or 1

        # Handle full-screen case when row and col are both 0
        if col == 0 and row == 0:
            return Position(
                x=self.monitor_info.x,
                y=self.monitor_info.y,
                width=self.monitor_info.width,
                height=self.monitor_info.height,
            )

        # Validate inputs for out-of-bounds rows and columns
        if row < 1 or row > self.rows:
            raise ValueError(f"Row {row} is out of bounds for grid with {self.rows} rows.")
        if col < 1 or col > self.cols:
            raise ValueError(f"Column {col} is out of bounds for grid with {self.cols} columns.")

        # Validate spans exceeding grid dimensions
        if row + row_span - 1 > self.rows:
            raise ValueError(f"Row span {row_span} exceeds grid dimensions.")
        if col + col_span - 1 > self.cols:
            raise ValueError(f"Column span {col_span} exceeds grid dimensions.")

        # Calculate pixel dimensions for each grid cell
        pixels_per_col = self.monitor_info.width / self.cols
        pixels_per_row = self.monitor_info.height / self.rows

        # Calculate starting pixel coordinates
        start_x = int(self.monitor_info.x + (col - 1) * pixels_per_col)
        start_y = int(self.monitor_info.y + (row - 1) * pixels_per_row)

        # Calculate the width and height of the spanned area
        width = int(col_span * pixels_per_col)
        height = int(row_span * pixels_per_row)

        # Return the resolved position
        return Position(
            x=start_x,
            y=start_y,
            width=width,
            height=height,
        )

