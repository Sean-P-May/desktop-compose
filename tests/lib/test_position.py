import pytest
from lib.position import Position

def test_position_addition():
    pos1 = Position(10, 20, 100, 200)
    pos2 = Position(5, 15, 50, 100)
    result = pos1 + pos2
    assert result.x == 15
    assert result.y == 35
    assert result.width == 150
    assert result.height == 300

def test_position_subtraction():
    pos1 = Position(10, 20, 100, 200)
    pos2 = Position(5, 15, 50, 100)
    result = pos1 - pos2
    assert result.x == 5
    assert result.y == 5
    assert result.width == 50
    assert result.height == 100

def test_position_iteration():
    pos = Position(10, 20, 100, 200)
    values = list(iter(pos))
    assert values == [10, 20, 100, 200]

def test_position_default_values():
    pos = Position()
    assert pos.x == 0
    assert pos.y == 0
    assert pos.width == 0
    assert pos.height == 0