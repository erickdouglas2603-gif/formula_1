"""Testes de f1.models.weather.Weather."""

from f1.models.weather import Weather


def test_from_api_converte_registro_completo(raw_weather):
    weather = Weather.from_api(raw_weather)

    assert weather.session_key == 9222
    assert weather.air_temperature == 22.5
    assert weather.track_temperature == 35.1
    assert weather.rainfall == 0
    assert weather.wind_direction == 180


def test_from_api_aceita_campos_opcionais_ausentes(raw_weather):
    del raw_weather["humidity"]
    del raw_weather["pressure"]

    weather = Weather.from_api(raw_weather)

    assert weather.humidity is None
    assert weather.pressure is None
