import pytest

from weather.weather_api import (
    ApiResponse,
    call_api,
    call_forecast_api,
    handling_multi_fuzzy_search_result,
)


@pytest.fixture
def search_list():
    return ["Taliwang", "Tawang", "Taiwan"]


def test_valid_input(monkeypatch, search_list):
    monkeypatch.setattr("weather.output.console.input", lambda _: "3")
    assert handling_multi_fuzzy_search_result(search_list, True) == "Taiwan"


def test_index_error_gt_max(monkeypatch, search_list):
    monkeypatch.setattr("weather.output.console.input", lambda _: "5")
    with pytest.raises(IndexError):
        handling_multi_fuzzy_search_result(search_list, True)


def test_value_error_str(monkeypatch, search_list):
    monkeypatch.setattr("weather.output.console.input", lambda _: "three")
    with pytest.raises(ValueError):
        handling_multi_fuzzy_search_result(search_list, True)


def test_value_error_float(monkeypatch, search_list):
    monkeypatch.setattr("weather.output.console.input", lambda _: "2.9")
    with pytest.raises(ValueError):
        handling_multi_fuzzy_search_result(search_list, True)


def test_call_api(mocker):
    mock_get = mocker.patch("weather.weather_api.requests.get")
    mock_get.return_value.json.return_value = {"cod": 200}
    result = call_api("taiwan")
    assert result == {"cod": 200}


def test_call_forecast_api(mocker):
    mock_get = mocker.patch("weather.weather_api.requests.get")
    mock_get.return_value.json.return_value = {
        "cod": 200,
        "coord": {"lon": 121, "lat": 24},
    }
    result = call_forecast_api("taiwan")
    assert result == ApiResponse(
        {"cod": 200, "coord": {"lon": 121, "lat": 24}}, "taiwan"
    )
