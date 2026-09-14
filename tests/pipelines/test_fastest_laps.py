"""Testes de f1.pipelines.fastest_laps."""

import pytest

from f1.pipelines.fastest_laps import (
    build_fastest_laps_by_circuit,
    iter_fastest_laps_by_circuit,
)


class FakeOpenF1Client:
    """Cliente falso que roteia respostas por endpoint e parâmetros."""

    def __init__(
        self, meetings, sessions_by_meeting, laps_by_session, drivers_by_session
    ):
        self._meetings = meetings
        self._sessions_by_meeting = sessions_by_meeting
        self._laps_by_session = laps_by_session
        self._drivers_by_session = drivers_by_session
        self.calls: list[tuple[str, dict]] = []

    def get(self, endpoint: str, params: dict | None = None) -> list[dict]:
        params = params or {}
        self.calls.append((endpoint, params))
        if endpoint == "meetings":
            return self._meetings
        if endpoint == "sessions":
            return self._sessions_by_meeting.get(params.get("meeting_key"), [])
        if endpoint == "laps":
            return self._laps_by_session.get(params.get("session_key"), [])
        if endpoint == "drivers":
            return self._drivers_by_session.get(params.get("session_key"), [])
        raise AssertionError(f"endpoint inesperado nos testes: {endpoint}")


def _spa_meeting():
    return {
        "meeting_key": 1219,
        "meeting_name": "Belgian Grand Prix",
        "circuit_short_name": "Spa-Francorchamps",
        "country_name": "Belgium",
        "year": 2023,
        "date_start": "2023-07-28T11:30:00+00:00",
    }


def _testing_meeting():
    return {
        "meeting_key": 1200,
        "meeting_name": "Pre-Season Testing",
        "circuit_short_name": "Bahrain",
        "country_name": "Bahrain",
        "year": 2023,
        "date_start": "2023-02-23T07:00:00+00:00",
    }


def _spa_race_session():
    return {
        "session_key": 9222,
        "meeting_key": 1219,
        "session_name": "Race",
        "session_type": "Race",
        "year": 2023,
        "country_name": "Belgium",
        "circuit_short_name": "Spa-Francorchamps",
    }


def test_build_fastest_laps_by_circuit_retorna_top_n_ordenado_por_duracao():
    client = FakeOpenF1Client(
        meetings=[_spa_meeting(), _testing_meeting()],
        sessions_by_meeting={1219: [_spa_race_session()], 1200: []},
        laps_by_session={
            9222: [
                {
                    "session_key": 9222,
                    "meeting_key": 1219,
                    "driver_number": 1,
                    "lap_number": 10,
                    "lap_duration": 106.456,
                    "is_pit_out_lap": False,
                },
                {
                    "session_key": 9222,
                    "meeting_key": 1219,
                    "driver_number": 44,
                    "lap_number": 12,
                    "lap_duration": 105.001,
                    "is_pit_out_lap": False,
                },
                {
                    "session_key": 9222,
                    "meeting_key": 1219,
                    "driver_number": 55,
                    "lap_number": 1,
                    "lap_duration": None,
                    "is_pit_out_lap": True,
                },
                {
                    "session_key": 9222,
                    "meeting_key": 1219,
                    "driver_number": 16,
                    "lap_number": 5,
                    "lap_duration": 110.2,
                    "is_pit_out_lap": False,
                },
            ]
        },
        drivers_by_session={
            9222: [
                {"driver_number": 1, "full_name": "Max VERSTAPPEN"},
                {"driver_number": 44, "broadcast_name": "L HAMILTON"},
                {"driver_number": 16, "full_name": "Charles LECLERC"},
            ]
        },
    )

    result = build_fastest_laps_by_circuit(2023, top_n=2, client=client)

    assert len(result) == 1
    circuit = result[0]
    assert circuit.circuit_short_name == "Spa-Francorchamps"
    assert circuit.session_key == 9222
    assert [entry.driver_number for entry in circuit.fastest_laps] == [44, 1]
    assert circuit.fastest_laps[0].driver_name == "L HAMILTON"
    assert circuit.fastest_laps[1].driver_name == "Max VERSTAPPEN"
    assert circuit.fastest_laps[0].lap_duration == 105.001


def test_build_fastest_laps_by_circuit_ignora_circuito_sem_sessao_do_tipo_pedido():
    client = FakeOpenF1Client(
        meetings=[_testing_meeting()],
        sessions_by_meeting={1200: []},
        laps_by_session={},
        drivers_by_session={},
    )

    result = build_fastest_laps_by_circuit(2023, client=client)

    assert result == []
    assert ("laps", {}) not in client.calls


def _monza_meeting():
    return {
        "meeting_key": 1300,
        "meeting_name": "Italian Grand Prix",
        "circuit_short_name": "Monza",
        "country_name": "Italy",
        "year": 2023,
        "date_start": "2023-09-01T11:30:00+00:00",
    }


def _monza_race_session():
    return {
        "session_key": 9333,
        "meeting_key": 1300,
        "session_name": "Race",
        "session_type": "Race",
        "year": 2023,
        "country_name": "Italy",
        "circuit_short_name": "Monza",
    }


def test_iter_fastest_laps_by_circuit_entrega_um_circuito_por_vez():
    client = FakeOpenF1Client(
        meetings=[_spa_meeting(), _monza_meeting()],
        sessions_by_meeting={
            1219: [_spa_race_session()],
            1300: [_monza_race_session()],
        },
        laps_by_session={
            9222: [
                {
                    "session_key": 9222,
                    "meeting_key": 1219,
                    "driver_number": 1,
                    "lap_number": 10,
                    "lap_duration": 106.456,
                    "is_pit_out_lap": False,
                }
            ],
            9333: [
                {
                    "session_key": 9333,
                    "meeting_key": 1300,
                    "driver_number": 1,
                    "lap_number": 20,
                    "lap_duration": 81.5,
                    "is_pit_out_lap": False,
                }
            ],
        },
        drivers_by_session={
            9222: [{"driver_number": 1, "full_name": "Max VERSTAPPEN"}],
            9333: [{"driver_number": 1, "full_name": "Max VERSTAPPEN"}],
        },
    )

    iterator = iter_fastest_laps_by_circuit(2023, client=client)

    first = next(iterator)
    assert first.circuit_short_name == "Spa-Francorchamps"
    # Só o primeiro circuito deve ter sido consultado até aqui: a entrega é
    # incremental, não espera a temporada inteira antes do primeiro yield.
    assert ("laps", {"session_key": 9333}) not in client.calls
    assert ("drivers", {"session_key": 9333}) not in client.calls

    second = next(iterator)
    assert second.circuit_short_name == "Monza"
    assert ("laps", {"session_key": 9333}) in client.calls

    with pytest.raises(StopIteration):
        next(iterator)


def test_build_fastest_laps_by_circuit_ignora_circuito_sem_voltas_validas():
    client = FakeOpenF1Client(
        meetings=[_spa_meeting()],
        sessions_by_meeting={1219: [_spa_race_session()]},
        laps_by_session={
            9222: [
                {
                    "session_key": 9222,
                    "meeting_key": 1219,
                    "driver_number": 1,
                    "lap_number": 1,
                    "lap_duration": None,
                    "is_pit_out_lap": True,
                }
            ]
        },
        drivers_by_session={9222: []},
    )

    result = build_fastest_laps_by_circuit(2023, client=client)

    assert result == []
