import pytest

from weather.weather_api import handling_multi_fuzzy_search_result


def create_fuzzy_search_list():
    return ["Taliwang", "Tawang", "Taiwan"]


def test_valid_input(monkeypatch):
    monkeypatch.setattr("weather.output.console.input", lambda _: "3")
    assert handling_multi_fuzzy_search_result(create_fuzzy_search_list()) == "Taiwan"


def test_index_error_gt_max(monkeypatch):
    monkeypatch.setattr("weather.output.console.input", lambda _: "5")
    with pytest.raises(IndexError):
        handling_multi_fuzzy_search_result(create_fuzzy_search_list())


def test_value_error_str(monkeypatch):
    monkeypatch.setattr("weather.output.console.input", lambda _: "three")
    with pytest.raises(ValueError):
        handling_multi_fuzzy_search_result(create_fuzzy_search_list())


def test_value_error_float(monkeypatch):
    monkeypatch.setattr("weather.output.console.input", lambda _: "2.9")
    with pytest.raises(ValueError):
        handling_multi_fuzzy_search_result(create_fuzzy_search_list())
