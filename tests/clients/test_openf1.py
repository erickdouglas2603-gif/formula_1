"""Testes de f1.clients.openf1.OpenF1Client (sem chamadas de rede reais)."""

import pytest
import requests

from f1.clients.exceptions import OpenF1RequestError
from f1.clients.openf1 import OpenF1Client


class FakeResponse:
    """Resposta HTTP falsa usada para simular `requests.Response` nos testes."""

    def __init__(self, json_data=None, status_code=200, json_error=None):
        self._json_data = json_data
        self.status_code = status_code
        self._json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._json_data


def test_get_retorna_lista_de_registros_quando_resposta_ok(monkeypatch):
    laps = [{"session_key": 9222, "driver_number": 1}]

    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(json_data=laps)

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client(base_url="https://api.openf1.org/v1/")
    result = client.get("laps", params={"session_key": 9222})

    assert result == laps


def test_get_usa_base_url_timeout_e_params_configurados(monkeypatch):
    captured = {}

    def fake_get(self, url, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse(json_data=[])

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client(base_url="https://exemplo.test/v1/", timeout_seconds=3.5)
    client.get("laps", params={"session_key": 9222, "driver_number": [1, 44]})

    assert captured["url"] == "https://exemplo.test/v1/laps"
    assert captured["params"] == {"session_key": 9222, "driver_number": [1, 44]}
    assert captured["timeout"] == 3.5


def test_get_envolve_timeout_em_openf1requesterror(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        raise requests.Timeout("timed out")

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client()
    with pytest.raises(OpenF1RequestError, match="laps"):
        client.get("laps")


def test_get_retorna_lista_vazia_quando_404_sem_resultados(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(status_code=404, json_data={"detail": "No results found."})

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client()
    result = client.get(
        "sessions", params={"meeting_key": 1228, "session_type": "Race"}
    )

    assert result == []


def test_get_tenta_novamente_em_429_e_retorna_apos_sucesso(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    def fake_get(self, url, params=None, timeout=None):
        calls["count"] += 1
        if calls["count"] < 3:
            return FakeResponse(status_code=429)
        return FakeResponse(json_data=[{"session_key": 9222}])

    monkeypatch.setattr(requests.Session, "get", fake_get)
    monkeypatch.setattr(
        "f1.clients.openf1.time.sleep", lambda seconds: sleeps.append(seconds)
    )

    client = OpenF1Client(backoff_seconds=1.0, min_interval_seconds=0.0)
    result = client.get("laps")

    assert result == [{"session_key": 9222}]
    assert calls["count"] == 3
    assert sleeps == [1.0, 2.0]


def test_get_levanta_erro_apos_esgotar_tentativas_em_429_persistente(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(status_code=429)

    monkeypatch.setattr(requests.Session, "get", fake_get)
    monkeypatch.setattr("f1.clients.openf1.time.sleep", lambda seconds: None)

    client = OpenF1Client(max_retries=2, backoff_seconds=0.01, min_interval_seconds=0.0)
    with pytest.raises(OpenF1RequestError, match="laps"):
        client.get("laps")


def test_get_respeita_intervalo_minimo_entre_requisicoes(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(json_data=[])

    monkeypatch.setattr(requests.Session, "get", fake_get)

    sleeps = []
    monkeypatch.setattr(
        "f1.clients.openf1.time.sleep", lambda seconds: sleeps.append(seconds)
    )
    monotonic_values = iter([100.0, 100.1, 100.2])
    monkeypatch.setattr(
        "f1.clients.openf1.time.monotonic", lambda: next(monotonic_values)
    )

    client = OpenF1Client(min_interval_seconds=1.0)
    client.get("laps")
    client.get("laps")

    assert sleeps == [pytest.approx(0.9)]


def test_get_envolve_http_error_em_openf1requesterror(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(status_code=500)

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client()
    with pytest.raises(OpenF1RequestError, match="laps"):
        client.get("laps")


def test_get_envolve_erro_de_rede_em_openf1requesterror(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client()
    with pytest.raises(OpenF1RequestError, match="laps"):
        client.get("laps")


def test_get_levanta_erro_quando_resposta_nao_e_lista(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(json_data={"detail": "not a list"})

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client()
    with pytest.raises(OpenF1RequestError, match="laps"):
        client.get("laps")


def test_get_levanta_erro_quando_json_invalido(monkeypatch):
    def fake_get(self, url, params=None, timeout=None):
        return FakeResponse(json_error=ValueError("json malformado"))

    monkeypatch.setattr(requests.Session, "get", fake_get)

    client = OpenF1Client()
    with pytest.raises(OpenF1RequestError, match="laps"):
        client.get("laps")
