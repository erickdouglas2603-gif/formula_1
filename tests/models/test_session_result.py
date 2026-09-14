"""Testes de f1.models.session_result.SessionResult."""

from f1.models.session_result import SessionResult


def test_from_api_converte_registro_completo(raw_session_result):
    result = SessionResult.from_api(raw_session_result)

    assert result.session_key == 9222
    assert result.driver_number == 1
    assert result.position == 1
    assert result.number_of_laps == 44
    assert result.dnf is False
    assert result.dns is False
    assert result.dsq is False


def test_from_api_marca_piloto_dnf_sem_posicao_final(raw_session_result):
    raw_session_result["position"] = None
    raw_session_result["dnf"] = True

    result = SessionResult.from_api(raw_session_result)

    assert result.position is None
    assert result.dnf is True
