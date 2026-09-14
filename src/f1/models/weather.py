"""Modelo de domínio do endpoint `weather` da OpenF1 API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from f1.utils.parsing import parse_datetime


@dataclass
class Weather:
    """Condições climáticas registradas durante a sessão.

    Attributes:
        session_key: identificador da sessão a que o registro se refere.
        meeting_key: identificador do fim de semana de Grande Prêmio.
        date: data/hora da medição.
        air_temperature: temperatura do ar, em °C.
        track_temperature: temperatura da pista, em °C.
        humidity: umidade relativa do ar, em %.
        pressure: pressão atmosférica, em mbar.
        rainfall: indica se há chuva (0 = não, 1 = sim).
        wind_direction: direção do vento, em graus (0-359).
        wind_speed: velocidade do vento, em m/s.
    """

    session_key: int
    meeting_key: int
    date: datetime | None
    air_temperature: float | None
    track_temperature: float | None
    humidity: float | None
    pressure: float | None
    rainfall: int | None
    wind_direction: int | None
    wind_speed: float | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Weather":
        """Converte um registro bruto do endpoint `weather` em `Weather`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `weather`.

        Returns:
            Instância de `Weather` correspondente.
        """
        return cls(
            session_key=data["session_key"],
            meeting_key=data["meeting_key"],
            date=parse_datetime(data.get("date")),
            air_temperature=data.get("air_temperature"),
            track_temperature=data.get("track_temperature"),
            humidity=data.get("humidity"),
            pressure=data.get("pressure"),
            rainfall=data.get("rainfall"),
            wind_direction=data.get("wind_direction"),
            wind_speed=data.get("wind_speed"),
        )
