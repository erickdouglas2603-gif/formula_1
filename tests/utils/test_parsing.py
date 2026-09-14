"""Testes de f1.utils.parsing."""

from datetime import datetime

import pytest

from f1.utils.parsing import parse_datetime


def test_parse_datetime_converte_iso_8601_valido():
    resultado = parse_datetime("2023-07-30T13:00:00+00:00")

    assert resultado == datetime.fromisoformat("2023-07-30T13:00:00+00:00")


@pytest.mark.parametrize("valor_ausente", [None, ""])
def test_parse_datetime_retorna_none_quando_valor_ausente(valor_ausente):
    assert parse_datetime(valor_ausente) is None


def test_parse_datetime_rejeita_formato_invalido():
    with pytest.raises(ValueError):
        parse_datetime("nao-e-uma-data")
