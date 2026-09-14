"""Testes de f1.models.driver.Driver."""

from f1.models.driver import Driver


def test_from_api_converte_registro_completo(raw_driver):
    driver = Driver.from_api(raw_driver)

    assert driver.driver_number == 1
    assert driver.session_key == 9222
    assert driver.meeting_key == 1219
    assert driver.broadcast_name == "M VERSTAPPEN"
    assert driver.full_name == "Max VERSTAPPEN"
    assert driver.first_name == "Max"
    assert driver.last_name == "Verstappen"
    assert driver.name_acronym == "VER"
    assert driver.team_name == "Red Bull Racing"
    assert driver.team_colour == "3671C6"
    assert driver.headshot_url == "https://example.com/verstappen.png"


def test_from_api_aceita_campos_opcionais_ausentes(raw_driver):
    del raw_driver["team_colour"]
    del raw_driver["headshot_url"]

    driver = Driver.from_api(raw_driver)

    assert driver.team_colour is None
    assert driver.headshot_url is None
