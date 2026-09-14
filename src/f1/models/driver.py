"""Modelo de domínio do endpoint `drivers` da OpenF1 API."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Driver:
    """Informações de um piloto em uma sessão.

    Attributes:
        driver_number: número do piloto (ex.: 1, 44, 55).
        session_key: identificador da sessão a que o registro se refere.
        meeting_key: identificador do fim de semana de Grande Prêmio.
        broadcast_name: nome usado na transmissão (ex.: `"M VERSTAPPEN"`).
        full_name: nome completo do piloto.
        first_name: primeiro nome do piloto.
        last_name: sobrenome do piloto.
        name_acronym: sigla de três letras (ex.: `"VER"`).
        team_name: nome da equipe.
        team_colour: cor da equipe, em hexadecimal sem `#` (ex.: `"3671C6"`).
        headshot_url: URL da foto de perfil do piloto.
    """

    driver_number: int
    session_key: int
    meeting_key: int
    broadcast_name: str | None
    full_name: str | None
    first_name: str | None
    last_name: str | None
    name_acronym: str | None
    team_name: str | None
    team_colour: str | None
    headshot_url: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Driver":
        """Converte um registro bruto do endpoint `drivers` em `Driver`.

        Args:
            data: dicionário retornado pela OpenF1 API para um item do
                endpoint `drivers`.

        Returns:
            Instância de `Driver` correspondente.
        """
        return cls(
            driver_number=data["driver_number"],
            session_key=data["session_key"],
            meeting_key=data["meeting_key"],
            broadcast_name=data.get("broadcast_name"),
            full_name=data.get("full_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            name_acronym=data.get("name_acronym"),
            team_name=data.get("team_name"),
            team_colour=data.get("team_colour"),
            headshot_url=data.get("headshot_url"),
        )
