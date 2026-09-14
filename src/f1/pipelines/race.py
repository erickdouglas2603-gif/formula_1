"""Pipeline de extração dos dados de uma corrida/sessão específica."""

import logging
from dataclasses import dataclass

from f1.clients.openf1 import OpenF1Client
from f1.models import Driver, Lap, Position, Session, SessionResult, Weather

logger = logging.getLogger(__name__)


class SessionNotFoundError(Exception):
    """Levantada quando `session_key` não corresponde a nenhuma sessão da OpenF1 API."""


@dataclass
class RaceDataset:
    """Conjunto de dados extraídos de uma sessão de corrida.

    Attributes:
        session: informações da sessão.
        drivers: pilotos que participaram da sessão.
        laps: voltas registradas na sessão.
        positions: posições de cada piloto ao longo da sessão.
        weather: condições climáticas registradas durante a sessão.
        results: classificação final da sessão.
    """

    session: Session
    drivers: list[Driver]
    laps: list[Lap]
    positions: list[Position]
    weather: list[Weather]
    results: list[SessionResult]


def build_race_dataset(
    session_key: int, client: OpenF1Client | None = None
) -> RaceDataset:
    """Constrói o `RaceDataset` de uma sessão a partir da OpenF1 API.

    Consulta os endpoints `sessions`, `drivers`, `laps`, `position`, `weather`
    e `session_result` filtrando por `session_key`, e converte cada resposta
    para os modelos de domínio correspondentes.

    Args:
        session_key: identificador da sessão a ser extraída.
        client: cliente da OpenF1 API a usar. Se omitido, um `OpenF1Client`
            padrão é criado (parâmetro pensado para facilitar testes com um
            cliente mockado).

    Returns:
        `RaceDataset` com os dados da sessão.

    Raises:
        SessionNotFoundError: se `session_key` não corresponder a nenhuma
            sessão retornada pela OpenF1 API.
        OpenF1RequestError: se alguma consulta à OpenF1 API falhar.
    """
    client = client or OpenF1Client()
    params = {"session_key": session_key}

    logger.info("Construindo RaceDataset para session_key=%s", session_key)

    sessions_data = client.get("sessions", params=params)
    if not sessions_data:
        raise SessionNotFoundError(
            f"Nenhuma sessão encontrada para session_key={session_key}"
        )
    session = Session.from_api(sessions_data[0])

    drivers = [Driver.from_api(item) for item in client.get("drivers", params=params)]
    laps = [Lap.from_api(item) for item in client.get("laps", params=params)]
    positions = [
        Position.from_api(item) for item in client.get("position", params=params)
    ]
    weather = [Weather.from_api(item) for item in client.get("weather", params=params)]
    results = [
        SessionResult.from_api(item)
        for item in client.get("session_result", params=params)
    ]

    return RaceDataset(
        session=session,
        drivers=drivers,
        laps=laps,
        positions=positions,
        weather=weather,
        results=results,
    )
