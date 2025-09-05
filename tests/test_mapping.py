import pytest

from weather.mappings import get_wind_direction


@pytest.mark.parametrize("arg, expected", [(90, "E (90°)"), (270, "W (270°)")])
def test_get_wind_direction_Ordinary_Angles(arg, expected):
    assert get_wind_direction(arg) == expected
