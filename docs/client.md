# Configuração e Cliente

## Configuração (`f1.config`)

A URL base da OpenF1 API e o timeout padrão de requisição são centralizados em
`f1.config` e lidos de variáveis de ambiente, nunca hardcoded:

| Variável | Descrição | Default |
|---|---|---|
| `OPENF1_BASE_URL` | URL base da OpenF1 API | `https://api.openf1.org/v1/` |
| `OPENF1_TIMEOUT_SECONDS` | Timeout de requisição, em segundos | `10.0` |

```python
from f1.config import get_settings

settings = get_settings()
settings.base_url  # "https://api.openf1.org/v1/"
settings.timeout_seconds  # 10.0
```

## Cliente da OpenF1 API (`f1.clients.openf1.OpenF1Client`)

`OpenF1Client` é um cliente HTTP fino sobre `requests`, com um único método
genérico de consulta usado para qualquer endpoint da API:

```python
from f1.clients.openf1 import OpenF1Client

client = OpenF1Client()
laps = client.get("laps", params={"session_key": 9222, "driver_number": 1})
```

- `params` aceita os filtros de query documentados em [API OpenF1](api.md):
  operadores de comparação embutidos no nome do parâmetro (ex.:
  `{"lap_duration>=": 120}`) e múltiplos valores por parâmetro via lista (ex.:
  `{"driver_number": [1, 44]}`).
- Erros de rede, timeout ou status HTTP de erro são sempre convertidos em
  `f1.clients.exceptions.OpenF1RequestError`, nunca vazando uma exceção genérica
  de `requests`.

### Peculiaridades observadas na OpenF1 API

- **HTTP 404 significa "sem resultados", não "erro"**: quando um filtro não
  encontra nenhum registro, a API responde com `404` em vez de `200` com uma
  lista vazia. `OpenF1Client.get` trata isso como resultado vazio (`[]`), não
  como exceção — do contrário, uma consulta legítima sem dados (ex.: uma
  sessão do tipo `"Race"` em um fim de semana de testes) derrubaria qualquer
  código que a chamasse.
- **Rate limiting (HTTP 429) sem `Retry-After`**: a API aplica rate limiting,
  mas não documenta o limite nem envia cabeçalhos `Retry-After`. Por isso o
  cliente se autolimita entre requisições (`min_interval_seconds`, padrão
  `1.0`s) e, se ainda assim receber `429`, tenta novamente com backoff
  exponencial (`max_retries`, padrão `5`; `backoff_seconds`, padrão `1.0`s —
  dobra a cada tentativa). Isso é essencial em pipelines que fazem muitas
  chamadas em sequência, como
  `f1.pipelines.fastest_laps.build_fastest_laps_by_circuit`.

Para usar uma URL base, timeout ou política de retry/rate-limit diferentes dos
padrões, passe-os explicitamente ao construtor:

```python
client = OpenF1Client(
    base_url="https://api.openf1.org/v1/",
    timeout_seconds=5.0,
    max_retries=5,
    backoff_seconds=1.0,
    min_interval_seconds=1.0,
)
```

::: f1.config
::: f1.clients.openf1
::: f1.clients.exceptions
