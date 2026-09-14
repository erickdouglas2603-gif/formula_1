"""Testes de f1.pipelines.race.build_race_dataset (com cliente mockado)."""

import pytest

from f1.pipelines.race import SessionNotFoundError, build_race_dataset


class FakeOpenF1Client:
    """Cliente falso que devolve respostas pré-definidas por endpoint."""

    def __init__(self, responses: dict[str, list[dict]]):
        self._responses = responses
        self.calls: list[tuple[str, dict]] = []

    def get(self, endpoint: str, params: dict | None = None) -> list[dict]:
        self.calls.append((endpoint, params or {}))
        return self._responses.get(endpoint, [])


@pytest.fixture
def responses(
    raw_session, raw_driver, raw_lap, raw_position, raw_weather, raw_session_result
):
    return {
        "sessions": [raw_session],
        "drivers": [raw_driver],
        "laps": [raw_lap],
        "position": [raw_position],
        "weather": [raw_weather],
        "session_result": [raw_session_result],
    }


def test_build_race_dataset_monta_dataset_completo(responses):
    client = FakeOpenF1Client(responses)

    dataset = build_race_dataset(9222, client=client)

    assert dataset.session.session_key == 9222
    assert len(dataset.drivers) == 1
    assert dataset.drivers[0].driver_number == 1
    assert len(dataset.laps) == 1
    assert len(dataset.positions) == 1
    assert len(dataset.weather) == 1
    assert len(dataset.results) == 1
    assert all(params == {"session_key": 9222} for _endpoint, params in client.calls)


def test_build_race_dataset_levanta_erro_quando_sessao_nao_existe(responses):
    responses["sessions"] = []
    client = FakeOpenF1Client(responses)

    with pytest.raises(SessionNotFoundError, match="9222"):
        build_race_dataset(9222, client=client)
