"""Modelo de domínio do endpoint `laps` da OpenF1 API."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from f1.utils.parsing import parse_datetime


@dataclass
class Lap:
    """Detalhes de uma volta individual de um piloto.

    Attributes:
        session_key: identificador da sessão a que o registro se refere.
        meeting_key: identificador do fim de semana de Grande Prêmio.
        driver_number: número do piloto.
        lap_number: número sequencial da volta.
        date_start: data/hora de início da volta.
        lap_duration: duração total da volta, em segundos (`None` quando não
            aplicável, ex.: volta de saída do pit lane).
        duration_sector_1: duração do setor 1, em segundos.
        duration_sector_2: duração do setor 2, em segundos.
        duration_sector_3: duração do setor 3, em segundos.
        i1_speed: velocidade no primeiro ponto de medição (speed trap), km/h.
        i2_speed: velocidade no segundo ponto de medição (speed trap), km/h.
        st_speed: velocidade na reta principal (speed trap), km/h.
        is_pit_out_lap: indica se a volta é uma saída do pit lane.
    """

    session_key: int
    meeting_key: int
    driver_number: int
    lap_number: int
    date_start: datetime | None
    lap_duration: float | None
    duration_sector_1: float | None
    duration_sector_2: float | None
    duration_sector_3: float | None
    i1_speed: float | None
    i2_speed: float | None
    st_speed: float | None
    is_pit_out_lap: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Lap":
        """Converte um registro bruto do endpoint `laps` em `Lap`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `laps`.

        Returns:
            Instância de `Lap` correspondente.
        """
        return cls(
            session_key=data["session_key"],
            meeting_key=data["meeting_key"],
            driver_number=data["driver_number"],
            lap_number=data["lap_number"],
            date_start=parse_datetime(data.get("date_start")),
            lap_duration=data.get("lap_duration"),
            duration_sector_1=data.get("duration_sector_1"),
            duration_sector_2=data.get("duration_sector_2"),
            duration_sector_3=data.get("duration_sector_3"),
            i1_speed=data.get("i1_speed"),
            i2_speed=data.get("i2_speed"),
            st_speed=data.get("st_speed"),
            is_pit_out_lap=bool(data.get("is_pit_out_lap", False)),
        )
