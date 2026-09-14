"""Exceções de domínio dos clientes de acesso a serviços externos."""


class OpenF1RequestError(Exception):
    """Erro ao consultar a OpenF1 API.

    Levantada para envolver falhas de rede, timeout, status HTTP de erro ou
    resposta em formato inesperado, para que o chamador nunca precise tratar
    exceções genéricas de `requests`.
    """
