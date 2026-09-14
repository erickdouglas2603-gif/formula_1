# Pipeline de extração

## Modelos de domínio (`f1.models`)

Cada endpoint do MVP tem uma `dataclass` correspondente, com um método de
classe `from_api` que converte o JSON bruto retornado pela OpenF1 API:

| Modelo | Endpoint da OpenF1 |
|---|---|
| `f1.models.Session` | `sessions` |
| `f1.models.Driver` | `drivers` |
| `f1.models.Lap` | `laps` |
| `f1.models.Position` | `position` |
| `f1.models.Weather` | `weather` |
| `f1.models.SessionResult` | `session_result` |

```python
from f1.models import Lap

lap = Lap.from_api({"session_key": 9222, "driver_number": 1, "lap_number": 1, ...})
```

## Rodando o pipeline (`f1.pipelines.race.build_race_dataset`)

`build_race_dataset` orquestra o cliente da OpenF1 API e os modelos acima para
montar um `RaceDataset` completo de uma sessão:

```python
from f1.pipelines.race import build_race_dataset

dataset = build_race_dataset(session_key=9222)

dataset.session  # f1.models.Session
dataset.drivers  # list[f1.models.Driver]
dataset.laps  # list[f1.models.Lap]
dataset.positions  # list[f1.models.Position]
dataset.weather  # list[f1.models.Weather]
dataset.results  # list[f1.models.SessionResult]
```

Se `session_key` não corresponder a nenhuma sessão retornada pela OpenF1 API,
`build_race_dataset` levanta `f1.pipelines.race.SessionNotFoundError`. Falhas
na comunicação com a API (rede, timeout, HTTP) levantam
`f1.clients.exceptions.OpenF1RequestError` (ver [Configuração e Cliente](client.md)).

Para testes ou usos avançados, um `f1.clients.openf1.OpenF1Client` já
configurado pode ser injetado explicitamente:

```python
from f1.clients.openf1 import OpenF1Client
from f1.pipelines.race import build_race_dataset

client = OpenF1Client(timeout_seconds=30.0)
dataset = build_race_dataset(session_key=9222, client=client)
```

O notebook `notebooks/analise_corrida.ipynb` consome `build_race_dataset`
diretamente em memória (sem persistência) para uma primeira análise
exploratória da sessão.

::: f1.models
::: f1.pipelines.race
