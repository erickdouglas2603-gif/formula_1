"""Modelo de domínio do endpoint `sessions` da OpenF1 API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from f1.utils.parsing import parse_datetime


@dataclass
class Session:
    """Informações de uma sessão (treino, classificação ou corrida).

    Attributes:
        session_key: identificador único da sessão.
        meeting_key: identificador do fim de semana de Grande Prêmio.
        session_name: nome da sessão (ex.: `"Race"`).
        session_type: tipo da sessão (ex.: `"Race"`, `"Practice"`).
        year: ano de disputa.
        country_name: nome do país onde a sessão ocorreu.
        circuit_short_name: nome curto do circuito.
        location: cidade/local do circuito.
        date_start: data/hora de início da sessão.
        date_end: data/hora de término da sessão.
        gmt_offset: deslocamento em relação ao GMT (ex.: `"02:00:00"`).
    """

    session_key: int
    meeting_key: int
    session_name: str
    session_type: str
    year: int
    country_name: str
    circuit_short_name: str
    location: str | None
    date_start: datetime | None
    date_end: datetime | None
    gmt_offset: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Session":
        """Converte um registro bruto do endpoint `sessions` em `Session`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `sessions`.

        Returns:
            Instância de `Session` correspondente.
        """
        return cls(
            session_key=data["session_key"],
            meeting_key=data["meeting_key"],
            session_name=data["session_name"],
            session_type=data["session_type"],
            year=data["year"],
            country_name=data["country_name"],
            circuit_short_name=data["circuit_short_name"],
            location=data.get("location"),
            date_start=parse_datetime(data.get("date_start")),
            date_end=parse_datetime(data.get("date_end")),
            gmt_offset=data.get("gmt_offset"),
        )
