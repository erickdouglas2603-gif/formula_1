"""Testes de f1.models.lap.Lap."""

from f1.models.lap import Lap


def test_from_api_converte_registro_completo(raw_lap):
    lap = Lap.from_api(raw_lap)

    assert lap.session_key == 9222
    assert lap.driver_number == 1
    assert lap.lap_number == 10
    assert lap.lap_duration == 106.456
    assert lap.duration_sector_1 == 30.1
    assert lap.is_pit_out_lap is False


def test_from_api_aceita_volta_de_saida_do_pit_sem_duracao(raw_lap):
    raw_lap["lap_duration"] = None
    raw_lap["duration_sector_1"] = None
    raw_lap["is_pit_out_lap"] = True

    lap = Lap.from_api(raw_lap)

    assert lap.lap_duration is None
    assert lap.duration_sector_1 is None
    assert lap.is_pit_out_lap is True


def test_from_api_aceita_is_pit_out_lap_ausente(raw_lap):
    del raw_lap["is_pit_out_lap"]

    lap = Lap.from_api(raw_lap)

    assert lap.is_pit_out_lap is False
