"""Testes de f1.models.meeting.Meeting."""

from f1.models.meeting import Meeting


def test_from_api_converte_registro_completo():
    raw_meeting = {
        "meeting_key": 1219,
        "meeting_name": "Belgian Grand Prix",
        "circuit_short_name": "Spa-Francorchamps",
        "country_name": "Belgium",
        "location": "Spa-Francorchamps",
        "year": 2023,
        "date_start": "2023-07-28T11:30:00+00:00",
    }

    meeting = Meeting.from_api(raw_meeting)

    assert meeting.meeting_key == 1219
    assert meeting.meeting_name == "Belgian Grand Prix"
    assert meeting.circuit_short_name == "Spa-Francorchamps"
    assert meeting.country_name == "Belgium"
    assert meeting.location == "Spa-Francorchamps"
    assert meeting.year == 2023
    assert meeting.date_start is not None


def test_from_api_aceita_campos_opcionais_ausentes():
    raw_meeting = {
        "meeting_key": 1219,
        "meeting_name": "Belgian Grand Prix",
        "circuit_short_name": "Spa-Francorchamps",
        "country_name": "Belgium",
        "year": 2023,
    }

    meeting = Meeting.from_api(raw_meeting)

    assert meeting.location is None
    assert meeting.date_start is None
