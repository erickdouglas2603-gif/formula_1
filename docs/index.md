# F1 Data Engineering

Projeto de engenharia de dados sobre a Fórmula 1, utilizando a [OpenF1 API](https://openf1.org/) como fonte de dados.

## Visão geral do pipeline

O pacote `f1` implementa um pipeline de ETL que reconstrói os dados de uma
corrida/sessão específica (identificada por um `session_key`) a partir da OpenF1
API:

1. **Configuração** (`f1.config`): URL base da API e timeout padrão, lidos de
   variáveis de ambiente — ver [Configuração e Cliente](client.md).
2. **Cliente** (`f1.clients.openf1.OpenF1Client`): consulta genérica a qualquer
   endpoint da API, com tratamento de erros de rede/HTTP — ver
   [Configuração e Cliente](client.md).
3. **Modelos de domínio** (`f1.models`): uma `dataclass` por endpoint do MVP
   (`Session`, `Driver`, `Lap`, `Position`, `Weather`, `SessionResult`), cada
   uma convertendo o JSON bruto da API via `from_api`.
4. **Pipeline de extração** (`f1.pipelines.race.build_race_dataset`): orquestra
   cliente e modelos para montar um `RaceDataset` completo de uma sessão — ver
   [Pipeline de extração](pipeline.md).
5. **Análise exploratória** (`notebooks/analise_corrida.ipynb`): consome o
   `RaceDataset` em memória (sem persistência) para visualizar ritmo de volta,
   evolução de posições, clima e resultado final de **uma** sessão.
6. **Ranking por temporada** (`f1.pipelines.fastest_laps.build_fastest_laps_by_circuit`):
   percorre todos os circuitos de uma temporada e extrai as voltas mais
   rápidas de cada um — é o dado que alimenta o **dashboard** (`dashboard/app.py`,
   Streamlit) — ver [Dashboard](dashboard.md).

O pipeline é genérico: qualquer `session_key`/temporada pode ser usado, nenhuma
corrida é fixada no código.

## Estrutura do projeto

- `src/f1/`: código-fonte do pacote `f1`.
- `tests/`: testes automatizados (pytest).
- `docs/`: documentação do projeto (MkDocs).
- `notebooks/`: análises exploratórias em Jupyter, fora do pacote `f1`.
- `dashboard/`: dashboard Streamlit, fora do pacote `f1`.

Veja [API OpenF1](api.md) para o resumo da API utilizada como fonte de dados.
