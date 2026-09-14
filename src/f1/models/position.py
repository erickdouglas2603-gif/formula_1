"""Modelo de domínio do endpoint `position` da OpenF1 API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from f1.utils.parsing import parse_datetime


@dataclass
class Position:
    """Posição de um piloto em um instante da sessão.

    Attributes:
        session_key: identificador da sessão a que o registro se refere.
        meeting_key: identificador do fim de semana de Grande Prêmio.
        driver_number: número do piloto.
        position: posição do piloto na corrida (1 = líder).
        date: data/hora em que a posição foi registrada.
    """

    session_key: int
    meeting_key: int
    driver_number: int
    position: int
    date: datetime | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Position":
        """Converte um registro bruto do endpoint `position` em `Position`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `position`.

        Returns:
            Instância de `Position` correspondente.
        """
        return cls(
            session_key=data["session_key"],
            meeting_key=data["meeting_key"],
            driver_number=data["driver_number"],
            position=data["position"],
            date=parse_datetime(data.get("date")),
        )
