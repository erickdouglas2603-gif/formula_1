"""Pipeline de extração das voltas mais rápidas por circuito, ao longo de uma
temporada.
"""

import logging
from collections.abc import Iterator
from dataclasses import dataclass

from f1.clients.openf1 import OpenF1Client
from f1.models import Lap, Meeting, Session

logger = logging.getLogger(__name__)

DEFAULT_TOP_N = 5
DEFAULT_SESSION_TYPE = "Race"


@dataclass
class FastestLapEntry:
    """Uma volta entre as mais rápidas de um circuito.

    Attributes:
        driver_number: número do piloto que fez a volta.
        driver_name: nome do piloto (usado para exibição).
        lap_number: número sequencial da volta.
        lap_duration: duração da volta, em segundos.
    """

    driver_number: int
    driver_name: str
    lap_number: int
    lap_duration: float


@dataclass
class CircuitFastestLaps:
    """As voltas mais rápidas registradas em um circuito/sessão.

    Attributes:
        meeting_key: identificador do fim de semana de Grande Prêmio.
        circuit_short_name: nome curto do circuito.
        country_name: nome do país onde o circuito está localizado.
        session_key: identificador da sessão de onde as voltas foram extraídas.
        fastest_laps: voltas mais rápidas do circuito, ordenadas da mais rápida
            para a mais lenta.
    """

    meeting_key: int
    circuit_short_name: str
    country_name: str
    session_key: int
    fastest_laps: list[FastestLapEntry]


def _driver_name(data: dict) -> str:
    """Resolve o nome de exibição de um piloto a partir do registro bruto da API."""
    return (
        data.get("full_name")
        or data.get("broadcast_name")
        or str(data.get("driver_number"))
    )


def _fastest_laps_for_session(
    client: OpenF1Client, session_key: int, top_n: int
) -> list[FastestLapEntry]:
    """Consulta voltas e pilotos de uma sessão e retorna as `top_n` mais rápidas."""
    laps = [
        Lap.from_api(item)
        for item in client.get("laps", params={"session_key": session_key})
        if item.get("lap_duration") is not None and not item.get("is_pit_out_lap")
    ]
    driver_names = {
        item["driver_number"]: _driver_name(item)
        for item in client.get("drivers", params={"session_key": session_key})
    }
    fastest = sorted(laps, key=lambda lap: lap.lap_duration)[:top_n]
    return [
        FastestLapEntry(
            driver_number=lap.driver_number,
            driver_name=driver_names.get(lap.driver_number, str(lap.driver_number)),
            lap_number=lap.lap_number,
            lap_duration=lap.lap_duration,
        )
        for lap in fastest
    ]


def iter_fastest_laps_by_circuit(
    year: int,
    top_n: int = DEFAULT_TOP_N,
    session_type: str = DEFAULT_SESSION_TYPE,
    client: OpenF1Client | None = None,
) -> Iterator[CircuitFastestLaps]:
    """Gera o ranking das voltas mais rápidas de cada circuito de uma temporada.

    Para cada fim de semana de Grande Prêmio (`meetings`) do ano informado,
    localiza a sessão do tipo `session_type` (por padrão, a corrida) e extrai
    as `top_n` voltas mais rápidas dessa sessão, com o nome do piloto que a
    completou. Circuitos sem sessão do tipo pedido (ex.: eventos de teste) são
    ignorados.

    Diferente de `build_fastest_laps_by_circuit`, esta função é um gerador:
    cada `CircuitFastestLaps` é entregue assim que fica pronto, sem esperar a
    temporada inteira ser consultada — útil para exibir resultados
    progressivamente (ex.: no dashboard) em vez de bloquear até o final.

    Args:
        year: ano da temporada a consultar.
        top_n: quantidade de voltas mais rápidas a retornar por circuito.
        session_type: tipo de sessão a considerar em cada circuito (ex.:
            `"Race"`, `"Qualifying"`).
        client: cliente da OpenF1 API a usar. Se omitido, um `OpenF1Client`
            padrão é criado (parâmetro pensado para facilitar testes com um
            cliente mockado).

    Yields:
        Um `CircuitFastestLaps` por circuito da temporada com sessão do tipo
        pedido, na ordem retornada pela OpenF1 API.
    """
    client = client or OpenF1Client()
    logger.info(
        "Construindo ranking de voltas mais rápidas para year=%s, session_type=%s",
        year,
        session_type,
    )

    meetings = [
        Meeting.from_api(item) for item in client.get("meetings", params={"year": year})
    ]

    for meeting in meetings:
        sessions_data = client.get(
            "sessions",
            params={"meeting_key": meeting.meeting_key, "session_type": session_type},
        )
        if not sessions_data:
            continue
        session = Session.from_api(sessions_data[0])
        fastest_laps = _fastest_laps_for_session(client, session.session_key, top_n)
        if not fastest_laps:
            continue
        yield CircuitFastestLaps(
            meeting_key=meeting.meeting_key,
            circuit_short_name=meeting.circuit_short_name,
            country_name=meeting.country_name,
            session_key=session.session_key,
            fastest_laps=fastest_laps,
        )


def build_fastest_laps_by_circuit(
    year: int,
    top_n: int = DEFAULT_TOP_N,
    session_type: str = DEFAULT_SESSION_TYPE,
    client: OpenF1Client | None = None,
) -> list[CircuitFastestLaps]:
    """Constrói o ranking das voltas mais rápidas de cada circuito de uma temporada.

    Equivalente a consumir `iter_fastest_laps_by_circuit` inteiramente em uma
    lista — use esta função quando quiser o resultado completo de uma vez;
    use `iter_fastest_laps_by_circuit` para processar/exibir cada circuito
    assim que ele fica pronto (ex.: um dashboard que atualiza
    progressivamente).

    Args:
        year: ano da temporada a consultar.
        top_n: quantidade de voltas mais rápidas a retornar por circuito.
        session_type: tipo de sessão a considerar em cada circuito (ex.:
            `"Race"`, `"Qualifying"`).
        client: cliente da OpenF1 API a usar. Se omitido, um `OpenF1Client`
            padrão é criado.

    Returns:
        Lista de `CircuitFastestLaps`, uma por circuito da temporada com
        sessão do tipo pedido, na ordem retornada pela OpenF1 API.
    """
    return list(
        iter_fastest_laps_by_circuit(
            year, top_n=top_n, session_type=session_type, client=client
        )
    )
