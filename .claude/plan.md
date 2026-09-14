# plan.md — Roteiro de Implementação do Projeto `f1`

Este documento é o roteiro de construção do projeto, complementar ao `SKILL.md`
(padrões e regras obrigatórias de desenvolvimento) e ao `doc_api.md`/`docs/api.md`
(referência da OpenF1 API, fonte de dados). Ele não repete regras já definidas em
`SKILL.md` — apenas referencia a seção aplicável.

## 1. Objetivo do projeto

Construir um **pipeline de dados (ETL)** sobre a [OpenF1 API](https://openf1.org/)
para reconstruir os dados de **uma corrida/GP específico** (sessão, pilotos, voltas,
posições, clima e resultado), e uma **camada de análise/visualização** sobre esses
dados extraídos.

O pipeline deve ser genérico o suficiente para funcionar com qualquer
`session_key`/`meeting_key` — nenhuma corrida específica fica hardcoded no código.

## 2. Escopo do MVP e decisões em aberto

**No escopo do MVP:**

- Endpoints da OpenF1 API (ver `docs/api.md`) para uma corrida específica:
  `sessions`, `drivers`, `laps`, `position`, `weather`, `session_result`.
  Opcionalmente, como enriquecimento: `starting_grid`, `pit`, `race_control`.
- Cliente da API, modelos de domínio e pipeline de extração, todos em `src/f1/`
  (cobertos por testes, seguindo `SKILL.md`).
- Uma análise/visualização inicial (notebook) consumindo o pipeline **em memória**,
  sem persistência.

**Decisão tomada ao final da Fase 5 (com caso de uso real em mãos):**

- **Entrega final do MVP**: dashboard Streamlit (`dashboard/app.py`) com o
  top N de voltas mais rápidas **por circuito**, para **todos os circuitos de
  uma temporada** (`f1.pipelines.fastest_laps.build_fastest_laps_by_circuit`).
  Isso amplia o item "múltiplas corridas / temporada completa" do Backlog
  (seção 5) de fora do MVP para dentro dele, especificamente para essa
  consulta agregada — o pipeline de uma sessão (`build_race_dataset`) e o
  notebook exploratório continuam existindo e cobrindo o caso de uma corrida
  específica.

**Fora do escopo do MVP (decisões adiadas de propósito):**

- **Persistência dos dados** (arquivos CSV/Parquet vs. SQLite vs. outro) — não
  decidido ainda. Cada execução do dashboard/notebook consulta a OpenF1 API em
  tempo real.
- Telemetria detalhada (`car_data`, `location`), campeonato
  (`championship_drivers`/`championship_teams`) — ver Backlog (seção 5).

## 3. Fases de implementação

Cada fase deve ser concluída seguindo o fluxo obrigatório e o checklist do
`SKILL.md` (§12 e §13) antes de passar para a próxima — ou seja, lint, testes com
cobertura ≥ 50% em `src/f1` e build da documentação são critério de "pronto" de
**cada fase**, não só do final do projeto.

### Fase 1 — Configuração
- **Arquivo**: `src/f1/config.py`
- Centraliza URL base da OpenF1 (`https://api.openf1.org/v1/`) e timeout padrão de
  requisição, lidos de variáveis de ambiente com defaults sensatos (`SKILL.md` §7 —
  configuração centralizada, nunca hardcoded/espalhada).

### Fase 2 — Cliente da API
- **Arquivos**: `src/f1/clients/openf1.py`, `src/f1/clients/exceptions.py`
- Cliente HTTP fino sobre `requests` com um método genérico de consulta
  (endpoint + parâmetros de query), suportando o padrão de filtros do
  `doc_api.md` (operadores `>=`, `<=`, `=`, múltiplos valores no mesmo parâmetro).
- Exceção de domínio `OpenF1RequestError` envolvendo erros de rede/HTTP (timeout,
  status de erro) — nunca deixar uma exceção genérica vazar (`SKILL.md` §7).

### Fase 3 — Modelos de domínio
- **Diretório**: `src/f1/models/`
- Uma `dataclass` tipada por endpoint do MVP: `Session`, `Driver`, `Lap`,
  `Position`, `Weather`, `SessionResult` — cada uma com um método
  `from_api(dict) -> T` para converter o JSON bruto da API.
- Sem dependência nova: `dataclasses` da stdlib resolvem o problema (evitar
  `pydantic` sem necessidade real — `SKILL.md` §6).

### Fase 4 — Pipeline de extração
- **Arquivo**: `src/f1/pipelines/race.py`
- Função de orquestração `build_race_dataset(session_key: int) -> RaceDataset`
  que consulta o cliente (Fase 2) para os endpoints do MVP e converte cada
  resposta usando os modelos (Fase 3), retornando um `RaceDataset` (dataclass
  agregadora com sessão, pilotos, voltas, posições, clima e resultado).
- Esta função é a fronteira testável entre "dados brutos da API" e "dados prontos
  para análise".

### Fase 5 — Análise/visualização (sem persistência)
- **Arquivo**: `notebooks/analise_corrida.ipynb` (fora de `src/f1/` — não entra na
  cobertura obrigatória de testes).
- Chama `build_race_dataset` diretamente em memória e produz visualizações
  exploratórias: ritmo de volta por piloto, evolução de posições ao longo da
  corrida, condições climáticas, resultado final.
- **Ao final desta fase**: revisitar com o usuário a decisão de persistência e de
  ferramenta de dashboard (seção 2), agora com um caso de uso real para embasar a
  escolha.

### Fase 6 — Testes
- `tests/clients/test_openf1.py` — mocka chamadas HTTP (nunca rede real).
- `tests/models/test_*.py` — parsing de JSON válido e casos de borda (campos
  ausentes/inválidos).
- `tests/pipelines/test_race.py` — orquestração com cliente mockado.
- Rodar `poetry run pytest` a cada fase concluída e confirmar cobertura ≥ 50% em
  `src/f1` (`SKILL.md` §10).

### Fase 7 — Documentação
- Atualizar `docs/index.md` com a visão geral do pipeline.
- Adicionar `docs/client.md` (uso do cliente OpenF1) e `docs/pipeline.md` (como
  rodar `build_race_dataset`), registrando ambos em `mkdocs.yml` (`nav`).
- Garantir que toda classe/função pública nova tem docstring estilo Google, para
  que `docs/reference.md` (mkdocstrings) reflita o código real (`SKILL.md` §7/§11).

## 4. Critério de "pronto" (por fase)

Reaproveita o checklist já definido em `SKILL.md` §13 — não duplicado aqui:

- `poetry run ruff check .` e `poetry run ruff format --check .` sem erros.
- `poetry run pytest` passando, cobertura de `src/f1` ≥ 50%.
- `poetry run mkdocs build --strict` sem erros, páginas novas no `nav`.
- Resumo final da fase: arquivos alterados + resultado de cada validação.

## 5. Backlog (fora do MVP)

- Persistência definitiva dos dados extraídos (arquivo local ou banco).
- Expandir para múltiplas corridas / temporada completa.
- Telemetria detalhada (`car_data`, `location`) e campeonato
  (`championship_drivers`, `championship_teams`).
- Dashboard interativo (se a escolha da Fase 5 apontar nessa direção).
- Agendamento/automação de execução periódica do pipeline.
