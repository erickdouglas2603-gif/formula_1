"""Testes de f1.config."""

import pytest

from f1 import config


def test_get_settings_usa_defaults_quando_sem_variaveis_de_ambiente(monkeypatch):
    monkeypatch.delenv("OPENF1_BASE_URL", raising=False)
    monkeypatch.delenv("OPENF1_TIMEOUT_SECONDS", raising=False)

    settings = config.get_settings()

    assert settings.base_url == config.DEFAULT_BASE_URL
    assert settings.timeout_seconds == config.DEFAULT_TIMEOUT_SECONDS


def test_get_settings_usa_variaveis_de_ambiente_quando_definidas(monkeypatch):
    monkeypatch.setenv("OPENF1_BASE_URL", "https://exemplo.test/v1/")
    monkeypatch.setenv("OPENF1_TIMEOUT_SECONDS", "5")

    settings = config.get_settings()

    assert settings.base_url == "https://exemplo.test/v1/"
    assert settings.timeout_seconds == 5.0


def test_get_settings_rejeita_timeout_invalido(monkeypatch):
    monkeypatch.setenv("OPENF1_TIMEOUT_SECONDS", "nao-numerico")

    with pytest.raises(ValueError):
        config.get_settings()
