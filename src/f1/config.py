"""Configuração centralizada do projeto f1.

Concentra a leitura de variáveis de ambiente usadas pelo pacote (URL base da
OpenF1 API, timeout padrão de requisição), para que nenhum outro módulo leia
`os.environ` diretamente.
"""

import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://api.openf1.org/v1/"
DEFAULT_TIMEOUT_SECONDS = 10.0


@dataclass(frozen=True)
class Settings:
    """Configuração efetiva do projeto.

    Attributes:
        base_url: URL base da OpenF1 API.
        timeout_seconds: timeout padrão, em segundos, para requisições HTTP.
    """

    base_url: str
    timeout_seconds: float


def get_settings() -> Settings:
    """Carrega a configuração do projeto a partir de variáveis de ambiente.

    Variáveis lidas:
        `OPENF1_BASE_URL`: URL base da OpenF1 API (default: `DEFAULT_BASE_URL`).
        `OPENF1_TIMEOUT_SECONDS`: timeout de requisição em segundos (default:
            `DEFAULT_TIMEOUT_SECONDS`).

    Returns:
        Settings com os valores lidos do ambiente (ou os defaults).
    """
    return Settings(
        base_url=os.getenv("OPENF1_BASE_URL", DEFAULT_BASE_URL),
        timeout_seconds=float(
            os.getenv("OPENF1_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
        ),
    )
