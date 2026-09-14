"""Modelo de domínio do endpoint `session_result` da OpenF1 API."""

from dataclasses import dataclass
from typing import Any


@dataclass
class SessionResult:
    """Classificação final de um piloto em uma sessão.

    Attributes:
        session_key: identificador da sessão a que o registro se refere.
        meeting_key: identificador do fim de semana de Grande Prêmio.
        driver_number: número do piloto.
        position: posição final do piloto na sessão.
        duration: tempo total (ou por segmento) do piloto na sessão, em
            segundos.
        gap_to_leader: diferença de tempo para o líder da sessão.
        number_of_laps: número de voltas completadas pelo piloto.
        dnf: indica se o piloto não terminou a sessão (Did Not Finish).
        dns: indica se o piloto não largou (Did Not Start).
        dsq: indica se o piloto foi desqualificado (Disqualified).
    """

    session_key: int
    meeting_key: int
    driver_number: int
    position: int | None
    duration: float | None
    gap_to_leader: float | None
    number_of_laps: int | None
    dnf: bool
    dns: bool
    dsq: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "SessionResult":
        """Converte um registro bruto do endpoint `session_result` em `SessionResult`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `session_result`.

        Returns:
            Instância de `SessionResult` correspondente.
        """
        return cls(
            session_key=data["session_key"],
            meeting_key=data["meeting_key"],
            driver_number=data["driver_number"],
            position=data.get("position"),
            duration=data.get("duration"),
            gap_to_leader=data.get("gap_to_leader"),
            number_of_laps=data.get("number_of_laps"),
            dnf=bool(data.get("dnf", False)),
            dns=bool(data.get("dns", False)),
            dsq=bool(data.get("dsq", False)),
        )
