"""Testes de f1.models.session.Session."""

from datetime import datetime

from f1.models.session import Session


def test_from_api_converte_registro_completo(raw_session):
    session = Session.from_api(raw_session)

    assert session.session_key == 9222
    assert session.meeting_key == 1219
    assert session.session_name == "Race"
    assert session.session_type == "Race"
    assert session.year == 2023
    assert session.country_name == "Belgium"
    assert session.circuit_short_name == "Spa-Francorchamps"
    assert session.location == "Spa-Francorchamps"
    assert session.date_start == datetime.fromisoformat("2023-07-30T13:00:00+00:00")
    assert session.date_end == datetime.fromisoformat("2023-07-30T15:00:00+00:00")
    assert session.gmt_offset == "02:00:00"


def test_from_api_aceita_campos_opcionais_ausentes(raw_session):
    del raw_session["location"]
    del raw_session["date_start"]
    del raw_session["date_end"]
    del raw_session["gmt_offset"]

    session = Session.from_api(raw_session)

    assert session.location is None
    assert session.date_start is None
    assert session.date_end is None
    assert session.gmt_offset is None
