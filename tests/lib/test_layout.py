import pytest
from lib.layout import Layout, Monitor, Location


def test_resolve_single_cell():
    """Test resolving a position for a single cell in the grid."""
    layout = Layout(rows=3, cols=3)
    monitor = Monitor(monitor_index=0, layout=layout)
    location = Location(row=1, col=1)
    position = monitor.resolve_position(location)
    assert position.x >= 0
    assert position.y >= 0
    assert position.width > 0
    assert position.height > 0


def test_resolve_spanned_area():
    """Test resolving a position for a spanned area in the grid."""
    layout = Layout(rows=4, cols=4)
    monitor = Monitor(monitor_index=0, layout=layout)
    location = Location(row=2, col=2, row_span=2, col_span=2)
    position = monitor.resolve_position(location)
    assert position.width > 0
    assert position.height > 0
    assert position.x < position.x + position.width  # Width is positive
    assert position.y < position.y + position.height  # Height is positive


def test_out_of_bounds_row():
    """Test handling of a location with a row out of bounds."""
    layout = Layout(rows=3, cols=3)
    monitor = Monitor(monitor_index=0, layout=layout)
    with pytest.raises(ValueError):
        monitor.resolve_position(Location(row=4, col=1))  # Row exceeds grid bounds


def test_span_exceeds_grid():
    """Test handling of a span that exceeds the grid dimensions."""
    layout = Layout(rows=3, cols=3)
    monitor = Monitor(monitor_index=0, layout=layout)
    with pytest.raises(ValueError):
        monitor.resolve_position(Location(row=1, col=1, row_span=4, col_span=4))  # Span too large


def test_full_screen_position():
    """Test resolving a full-screen position when no location is provided."""
    layout = Layout(rows=3, cols=3)
    monitor = Monitor(monitor_index=0, layout=layout)
    position = monitor.resolve_position(None)  # Full-screen mode
    assert position.width == monitor.monitor_info.width
    assert position.height == monitor.monitor_info.height
