"""Testes de f1.models.position.Position."""

from f1.models.position import Position


def test_from_api_converte_registro_completo(raw_position):
    position = Position.from_api(raw_position)

    assert position.session_key == 9222
    assert position.driver_number == 1
    assert position.position == 1
    assert position.date is not None


def test_from_api_aceita_date_ausente(raw_position):
    del raw_position["date"]

    position = Position.from_api(raw_position)

    assert position.date is None
