# F1 — Engenharia de Dados

Pipeline de engenharia de dados sobre a Fórmula 1, usando a [OpenF1 API](https://openf1.org/) como fonte de dados. Extrai dados de sessões (voltas, posições, clima, resultados), monta datasets analíticos e os disponibiliza via notebook de análise exploratória e dashboard interativo.

## Visão geral

O pacote `f1` reconstrói os dados de uma corrida/sessão específica a partir da OpenF1 API, em etapas:

1. **Configuração** (`f1.config`) — URL base da API e timeout, lidos de variáveis de ambiente.
2. **Cliente HTTP** (`f1.clients.openf1.OpenF1Client`) — consulta genérica a qualquer endpoint da API, com retry/backoff para rate limiting.
3. **Modelos de domínio** (`f1.models`) — uma `dataclass` por endpoint (`Session`, `Driver`, `Lap`, `Position`, `Weather`, `SessionResult`).
4. **Pipeline de extração** (`f1.pipelines.race`) — monta um `RaceDataset` completo de uma sessão.
5. **Ranking por temporada** (`f1.pipelines.fastest_laps`) — percorre todos os circuitos de uma temporada e extrai as voltas mais rápidas de cada um; é o dado que alimenta o dashboard.

O pipeline é genérico: qualquer `session_key`/temporada pode ser usado, nenhuma corrida é fixada no código.

Documentação completa (arquitetura, API, referência de código) em [`docs/`](docs/), publicada via MkDocs Material.

## Estrutura do projeto

```
src/f1/           pacote principal (config, cliente HTTP, modelos, pipelines)
tests/            testes automatizados (pytest), espelhando a estrutura de src/f1
docs/             documentação do projeto (MkDocs Material)
notebooks/        análise exploratória em Jupyter (fora do pacote f1)
dashboard/        dashboard Streamlit (fora do pacote f1)
.claude/SKILL.md  padrões de desenvolvimento do projeto
```

## Requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/)

## Instalação

```bash
poetry install --with dev,notebooks,dashboard
```

## Uso

Tarefas comuns são expostas via [Taskipy](https://github.com/taskipy/taskipy) (`poetry run task <nome>`):

| Comando                       | Descrição                                    |
| ------------------------------ | --------------------------------------------- |
| `poetry run task test`         | roda a suíte de testes com cobertura          |
| `poetry run task lint`         | roda o lint (`ruff check`)                    |
| `poetry run task format`       | formata o código (`ruff format`)              |
| `poetry run task docs`         | build estático da documentação (`docs/` → `site/`) |
| `poetry run task docs-serve`   | serve a documentação localmente com live-reload |
| `poetry run task dashboard`    | roda o dashboard Streamlit                    |

Para explorar os dados interativamente, abra `notebooks/analise_corrida.ipynb` com `poetry run jupyter lab`.

## Documentação e padrões

- Documentação do projeto: [`docs/`](docs/) (via `poetry run task docs-serve`).
- Padrões de desenvolvimento (obrigatórios para qualquer alteração no código): [`.claude/SKILL.md`](.claude/SKILL.md).
