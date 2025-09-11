from datetime import datetime, timedelta

import pytest

from weather.mappings import (
    fuzzy_search,
    get_five_days_for_forecast,
    get_wind_direction,
)


@pytest.fixture
def current_day():
    return datetime.now()


@pytest.mark.parametrize("arg, expected", [(90, "E (90°)"), (270, "W (270°)")])
def test_get_wind_direction_ordinary_angles(arg, expected):
    assert get_wind_direction(arg) == expected


@pytest.mark.parametrize("arg, expected", [(169, "SSE (169°)"), (272, "WNW (272°)")])
def test_get_wind_direction_specific_angles(arg, expected):
    assert get_wind_direction(arg) == expected


@pytest.mark.parametrize(
    "arg, expected",
    [(-10, "(Invalid wind direction)"), (390, "(Invalid wind direction)")],
)
def test_get_wind_direction_invalid_angles(arg, expected):
    assert get_wind_direction(arg) == expected


def test_fuzzy_search_no_matching_result():
    assert fuzzy_search("!") == []


def test_get_five_days_for_forecast(current_day):
    test = [current_day + timedelta(day) for day in range(5)]
    print(str(test))
    assert get_five_days_for_forecast() == [
        str(current_day + timedelta(day))[:10] for day in range(5)
    ]
