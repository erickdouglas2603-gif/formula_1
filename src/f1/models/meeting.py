"""Modelo de domínio do endpoint `meetings` da OpenF1 API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from f1.utils.parsing import parse_datetime


@dataclass
class Meeting:
    """Informações de um fim de semana de Grande Prêmio (um circuito/evento).

    Attributes:
        meeting_key: identificador do fim de semana de Grande Prêmio.
        meeting_name: nome do evento (ex.: `"Belgian Grand Prix"`).
        circuit_short_name: nome curto do circuito (ex.: `"Spa-Francorchamps"`).
        country_name: nome do país onde o circuito está localizado.
        location: cidade/local do circuito.
        year: ano de disputa.
        date_start: data/hora de início do fim de semana.
    """

    meeting_key: int
    meeting_name: str
    circuit_short_name: str
    country_name: str
    location: str | None
    year: int
    date_start: datetime | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Meeting":
        """Converte um registro bruto do endpoint `meetings` em `Meeting`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `meetings`.

        Returns:
            Instância de `Meeting` correspondente.
        """
        return cls(
            meeting_key=data["meeting_key"],
            meeting_name=data["meeting_name"],
            circuit_short_name=data["circuit_short_name"],
            country_name=data["country_name"],
            location=data.get("location"),
            year=data["year"],
            date_start=parse_datetime(data.get("date_start")),
        )
