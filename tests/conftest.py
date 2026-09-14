"""Fixtures compartilhadas entre os testes do pacote f1."""

import pytest


@pytest.fixture
def raw_session() -> dict:
    """Registro bruto de exemplo do endpoint `sessions`."""
    return {
        "session_key": 9222,
        "meeting_key": 1219,
        "session_name": "Race",
        "session_type": "Race",
        "year": 2023,
        "country_name": "Belgium",
        "circuit_short_name": "Spa-Francorchamps",
        "location": "Spa-Francorchamps",
        "date_start": "2023-07-30T13:00:00+00:00",
        "date_end": "2023-07-30T15:00:00+00:00",
        "gmt_offset": "02:00:00",
    }


@pytest.fixture
def raw_driver() -> dict:
    """Registro bruto de exemplo do endpoint `drivers`."""
    return {
        "driver_number": 1,
        "session_key": 9222,
        "meeting_key": 1219,
        "broadcast_name": "M VERSTAPPEN",
        "full_name": "Max VERSTAPPEN",
        "first_name": "Max",
        "last_name": "Verstappen",
        "name_acronym": "VER",
        "team_name": "Red Bull Racing",
        "team_colour": "3671C6",
        "headshot_url": "https://example.com/verstappen.png",
    }


@pytest.fixture
def raw_lap() -> dict:
    """Registro bruto de exemplo do endpoint `laps`."""
    return {
        "session_key": 9222,
        "meeting_key": 1219,
        "driver_number": 1,
        "lap_number": 10,
        "date_start": "2023-07-30T13:32:00.123000+00:00",
        "lap_duration": 106.456,
        "duration_sector_1": 30.1,
        "duration_sector_2": 40.2,
        "duration_sector_3": 36.156,
        "i1_speed": 310,
        "i2_speed": 298,
        "st_speed": 320,
        "is_pit_out_lap": False,
    }


@pytest.fixture
def raw_position() -> dict:
    """Registro bruto de exemplo do endpoint `position`."""
    return {
        "session_key": 9222,
        "meeting_key": 1219,
        "driver_number": 1,
        "position": 1,
        "date": "2023-07-30T13:32:00+00:00",
    }


@pytest.fixture
def raw_weather() -> dict:
    """Registro bruto de exemplo do endpoint `weather`."""
    return {
        "session_key": 9222,
        "meeting_key": 1219,
        "date": "2023-07-30T13:00:00+00:00",
        "air_temperature": 22.5,
        "track_temperature": 35.1,
        "humidity": 60,
        "pressure": 1013.1,
        "rainfall": 0,
        "wind_direction": 180,
        "wind_speed": 1.8,
    }


@pytest.fixture
def raw_session_result() -> dict:
    """Registro bruto de exemplo do endpoint `session_result`."""
    return {
        "session_key": 9222,
        "meeting_key": 1219,
        "driver_number": 1,
        "position": 1,
        "duration": 5432.123,
        "gap_to_leader": 0.0,
        "number_of_laps": 44,
        "dnf": False,
        "dns": False,
        "dsq": False,
    }
