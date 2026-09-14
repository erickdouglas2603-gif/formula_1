"""Cliente HTTP para a OpenF1 API."""

import logging
import time
from typing import Any

import requests

from f1.clients.exceptions import OpenF1RequestError
from f1.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SECONDS = 1.0
DEFAULT_MIN_INTERVAL_SECONDS = 1.0


class OpenF1Client:
    """Cliente HTTP fino sobre a OpenF1 API.

    Expõe um único método genérico de consulta (`get`), usado por qualquer
    endpoint da API, e concentra o tratamento de erros de rede/HTTP. Como a
    OpenF1 API aplica rate limiting (HTTP 429) sem documentar o limite exato,
    o cliente se autolimita, espaçando requisições consecutivas, e ainda assim
    tenta novamente com backoff exponencial caso o limite seja atingido.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
        min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    ) -> None:
        """Inicializa o cliente.

        Args:
            base_url: URL base da OpenF1 API. Se omitido, usa a configuração
                centralizada em `f1.config.get_settings`.
            timeout_seconds: timeout padrão de requisição, em segundos. Se
                omitido, usa a configuração centralizada em
                `f1.config.get_settings`.
            max_retries: número máximo de novas tentativas quando a API
                responde com HTTP 429 (rate limit), sem contar a tentativa
                inicial.
            backoff_seconds: tempo de espera, em segundos, antes da primeira
                nova tentativa; dobra a cada tentativa subsequente (backoff
                exponencial).
            min_interval_seconds: intervalo mínimo, em segundos, entre o
                início de requisições consecutivas feitas por este cliente —
                autolimitação proativa para evitar atingir o rate limit da
                OpenF1 API em consultas com muitas chamadas em sequência (ex.:
                `f1.pipelines.fastest_laps.build_fastest_laps_by_circuit`).
        """
        settings = get_settings()
        self._base_url = (base_url or settings.base_url).rstrip("/")
        self._timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.timeout_seconds
        )
        self._max_retries = max_retries
        self._backoff_seconds = backoff_seconds
        self._min_interval_seconds = min_interval_seconds
        self._last_request_at: float | None = None
        self._session = requests.Session()

    def _wait_for_rate_limit(self) -> None:
        """Espaça o início desta requisição da anterior em `min_interval_seconds`."""
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self._min_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Consulta um endpoint da OpenF1 API e retorna os registros retornados.

        Args:
            endpoint: nome do endpoint, sem barra inicial (ex.: `"laps"`,
                `"sessions"`).
            params: parâmetros de query. Chaves podem incluir um operador de
                comparação suportado pela API (ex.: `{"lap_duration>=": 120}`
                para o filtro `lap_duration>=120`). Valores do tipo lista ou
                tupla geram múltiplas ocorrências do mesmo parâmetro na query
                string (filtro por múltiplos valores).

        Returns:
            Lista de registros (dicts) retornados pela API. A OpenF1 API
            responde com HTTP 404 (em vez de uma lista vazia) quando os
            filtros aplicados não encontram nenhum registro — esse caso é
            tratado como resultado vazio, não como erro.

        Raises:
            OpenF1RequestError: se a requisição falhar (timeout, erro de rede,
                status HTTP de erro diferente de 404, ou rate limit persistente
                após `max_retries` tentativas) ou se a resposta não puder ser
                interpretada como uma lista JSON.
        """
        url = f"{self._base_url}/{endpoint.lstrip('/')}"

        attempt = 0
        while True:
            self._wait_for_rate_limit()
            logger.info("Consultando endpoint '%s' da OpenF1 API", endpoint)
            try:
                response = self._session.get(
                    url, params=params, timeout=self._timeout_seconds
                )
            except requests.Timeout as exc:
                raise OpenF1RequestError(
                    f"Timeout ao consultar o endpoint '{endpoint}'"
                ) from exc
            except requests.RequestException as exc:
                raise OpenF1RequestError(
                    f"Erro de rede ao consultar o endpoint '{endpoint}': {exc}"
                ) from exc
            finally:
                self._last_request_at = time.monotonic()

            if response.status_code == 404:
                return []

            if response.status_code == 429 and attempt < self._max_retries:
                wait_seconds = self._backoff_seconds * (2**attempt)
                logger.warning(
                    "Rate limit da OpenF1 API no endpoint '%s'; aguardando %.1fs "
                    "antes da tentativa %d/%d",
                    endpoint,
                    wait_seconds,
                    attempt + 1,
                    self._max_retries,
                )
                time.sleep(wait_seconds)
                attempt += 1
                continue

            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise OpenF1RequestError(
                    f"Erro HTTP ao consultar o endpoint '{endpoint}': {exc}"
                ) from exc

            try:
                data = response.json()
            except ValueError as exc:
                raise OpenF1RequestError(
                    f"Resposta com JSON inválido do endpoint '{endpoint}'"
                ) from exc

            if not isinstance(data, list):
                raise OpenF1RequestError(
                    f"Resposta inesperada do endpoint '{endpoint}': "
                    "esperada uma lista JSON"
                )
            return data
