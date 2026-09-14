"""Conversões compartilhadas entre os modelos de domínio ao interpretar o JSON
bruto retornado pela OpenF1 API.
"""

from datetime import datetime


def parse_datetime(raw: str | None) -> datetime | None:
    """Converte uma data/hora ISO 8601 retornada pela API em `datetime`.

    Args:
        raw: valor bruto do campo de data (ex.: `"2023-05-07T18:52:51.301000+00:00"`),
            ou `None` quando o campo não foi retornado pela API.

    Returns:
        `datetime` correspondente, ou `None` se `raw` for `None` ou vazio.

    Raises:
        ValueError: se `raw` não estiver em um formato ISO 8601 reconhecido.
    """
    if not raw:
        return None
    return datetime.fromisoformat(raw)
