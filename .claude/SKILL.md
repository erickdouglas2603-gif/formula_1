---
name: f1-dev-standards
description: Guia obrigatório de desenvolvimento do projeto f1 — ambiente, dependências, arquitetura, testes, cobertura e documentação
---

# SKILL.md — Padrões de Desenvolvimento do Projeto `f1`

## 1. Objetivo

Este documento é o guia obrigatório de desenvolvimento para qualquer IA (ou pessoa)
que crie, modifique ou revise código neste repositório. Ele define ambiente,
ferramentas, arquitetura, padrões de código, testes, cobertura e documentação.
Nenhuma tarefa neste projeto é considerada concluída sem seguir as regras aqui
descritas.

Sempre que houver dúvida sobre "como fazer algo neste projeto", a resposta deve vir
deste documento e da inspeção da estrutura existente — não de suposições ou de
padrões genéricos de outros projetos.

## 2. Contexto do projeto

- Projeto de **Engenharia de Dados** cujo domínio é dados de Fórmula 1, consumidos a
  partir da [OpenF1 API](https://openf1.org/) (ver `docs/api.md` / `doc_api.md`).
- Código principal em **`src/f1/`** (pacote Python `f1`, instalado via Poetry em
  modo editável).
- Testes em **`tests/`**, documentação em **`docs/`** (MkDocs).
- Estado atual: projeto em fase inicial (esqueleto de pacote). As convenções abaixo
  devem ser aplicadas desde o primeiro módulo real adicionado.
- Prioridades de projeto, em ordem: **corretude dos dados > legibilidade e
  manutenibilidade > performance prematura**. Não otimize antes de ter um motivo
  concreto (dataset grande, chamada de API lenta medida, etc.).
- **Peculiaridades conhecidas da OpenF1 API** (já tratadas em
  `f1.clients.openf1.OpenF1Client` — ver `docs/client.md`): um filtro sem
  resultados responde com HTTP 404 em vez de uma lista vazia; e a API aplica
  rate limiting (HTTP 429) sem documentar o limite nem enviar `Retry-After`.
  Qualquer novo código que chame a API diretamente (fora do `OpenF1Client`)
  precisa lidar com os dois casos.

## 3. Princípios de desenvolvimento

1. **Analise antes de criar.** Antes de adicionar um módulo, função, dependência ou
   configuração, verifique se algo equivalente já existe no projeto e reutilize.
2. **Simplicidade sobre generalidade.** Não crie abstrações, interfaces ou camadas
   "para o futuro". Resolva o problema atual da forma mais direta e legível possível.
3. **Baixo acoplamento, alta coesão.** Cada módulo deve ter um motivo único para
   mudar. Se um arquivo cresce demais ou mistura responsabilidades, divida-o.
4. **Sem duplicação.** Se a mesma lógica aparece em dois lugares, extraia-a para um
   ponto compartilhado — mas só na segunda ocorrência real, não preventivamente.
5. **Testabilidade como critério de design.** Se uma função é difícil de testar
   (depende de estado global, faz I/O escondido), isso é sinal para refatorar o
   design, não para pular o teste.
6. **Consistência com o que já existe.** Ao dúvida entre duas formas válidas de
   fazer algo, escolha a que já é usada no restante do projeto.

## 4. Estrutura do projeto

```
f1/
├── src/
│   └── f1/                # pacote instalável — TODO código de produção vive aqui
│       └── __init__.py
├── tests/                 # testes pytest, espelhando o caminho de src/f1/
│   └── __init__.py
├── notebooks/             # análises exploratórias (Jupyter) — fora de src/f1/,
│                          # não entram na cobertura obrigatória de testes
├── dashboard/             # dashboard Streamlit — fora de src/f1/, mesma regra
│                          # de cobertura das notebooks (lógica testada vem de src/f1/)
├── docs/                  # documentação (MkDocs)
│   ├── index.md
│   ├── api.md             # referência da OpenF1 API (fonte de dados)
│   └── reference.md       # referência de código autogerada (mkdocstrings)
├── mkdocs.yml
├── pyproject.toml         # Poetry + config de Ruff, pytest e coverage
├── poetry.lock
├── .python-version        # versão do Python fixada via pyenv (3.12.10)
└── SKILL.md               # este documento
```

### Organização interna de `src/f1/`

O pacote deve crescer por **responsabilidade**, não por acúmulo em um único arquivo.
Como referência (crie cada pasta apenas quando houver conteúdo real para colocar
nela — não crie pacotes vazios "por padrão"):

| Camada | Propósito | Exemplo |
|---|---|---|
| `f1/config.py` | Configuração e variáveis de ambiente | URL base da API, timeouts |
| `f1/clients/` | Acesso a serviços externos (infraestrutura) | cliente HTTP da OpenF1 |
| `f1/domain/` ou `f1/models/` | Entidades e regras de negócio | `Driver`, `Session`, `Lap` |
| `f1/pipelines/` (ou `etl/`) | Extração, transformação e carga de dados | funções de ingestão/parsing |
| `f1/utils/` | Utilitários genéricos e reutilizáveis | formatação de datas, retries |

Regras:

- Não misture acesso a dados externos (HTTP, arquivos, banco) com regras de negócio
  no mesmo módulo.
- Um módulo `utils.py` não deve virar um catálogo de funções sem relação entre si —
  se crescer, divida por domínio (`utils/time.py`, `utils/text.py`, etc.).
- Ao adicionar uma nova pasta/camada, atualize esta tabela no `SKILL.md` no mesmo
  commit.

## 5. Gerenciamento do ambiente (pyenv + Poetry)

- A versão do Python do projeto é fixada em **`.python-version`** (atualmente
  `3.12.10`) e declarada em `pyproject.toml` como `python = "^3.12"`. Essas duas
  fontes devem sempre ser compatíveis entre si.
- Nunca use uma versão de Python diferente da definida pelo pyenv para rodar
  comandos do projeto.
- Setup inicial em uma máquina nova:
  ```bash
  pyenv install --skip-existing $(cat .python-version)
  pyenv local $(cat .python-version)      # já está commitado, mas garante o shim ativo
  poetry env use $(cat .python-version)
  poetry install
  ```
- Todo comando do projeto roda **dentro** da venv gerenciada pelo Poetry:
  ```bash
  poetry run <comando>      # ex.: poetry run pytest
  # ou
  poetry shell               # entra no shell da venv
  ```
- **Nunca** crie uma venv manualmente (`python -m venv`) nem ative um interpretador
  fora do gerenciado pelo Poetry. Se precisar recriar o ambiente do zero:
  ```bash
  poetry env remove --all
  poetry env use $(cat .python-version)
  poetry install
  ```

## 6. Gerenciamento de dependências (Poetry — nunca pip)

- **Proibido usar `pip install`/`pip uninstall`** neste projeto, em qualquer
  circunstância. Toda dependência é declarada e instalada via Poetry.
- Adicionar dependência de produção:
  ```bash
  poetry add <pacote>
  ```
- Adicionar dependência de desenvolvimento (lint, testes, docs — nunca importada por
  código de produção):
  ```bash
  poetry add --group dev <pacote>
  ```
- Remover dependência:
  ```bash
  poetry remove [--group dev] <pacote>
  ```
- Instalar dependências já declaradas (ex.: após clonar o repo ou puxar mudanças):
  ```bash
  poetry install
  ```
- **Nunca edite `poetry.lock` manualmente.** Se editar `pyproject.toml` à mão, rode
  `poetry lock` antes de `poetry install`. Sempre versione `pyproject.toml` e
  `poetry.lock` juntos no mesmo commit.
- Antes de adicionar uma dependência nova, verifique em `pyproject.toml` se alguma
  já instalada não resolve o problema (evite duas libs para a mesma finalidade, ex.:
  duas libs de HTTP client).
- Dependências atuais do grupo `dev`: `ruff`, `pytest`, `pytest-cov`, `mkdocs`,
  `mkdocs-material`, `mkdocstrings[python]`, `taskipy` (atalhos de comando —
  ver seção 14).
- Dependências atuais do grupo `notebooks` (usadas só em `notebooks/`, nunca
  importadas por `src/f1/`): `jupyter`, `matplotlib`.
- Dependências atuais do grupo `dashboard` (usadas só em `dashboard/`, nunca
  importadas por `src/f1/`): `streamlit`.

## 7. Padrões de código Python

- **PEP 8** e sintaxe moderna de Python 3.12 (o Ruff cobre a maior parte da
  verificação automática — ver seção 8).
- **Type hints obrigatórios** em assinaturas de funções e métodos públicos
  (parâmetros e retorno). Use os tipos nativos modernos (`list[str]`, `dict[str,
  int]`, `str | None`) em vez de `typing.List`/`typing.Optional`.
- **Docstrings** (estilo Google) em todo módulo, classe e função pública — são a
  fonte do `docs/reference.md` gerado via mkdocstrings. Funções privadas (`_nome`)
  só precisam de docstring se o comportamento não for óbvio pelo nome/corpo.
  ```python
  def parse_lap_duration(raw: str) -> float:
      """Converte a duração de volta retornada pela API em segundos.

      Args:
          raw: valor bruto retornado pelo endpoint `laps` (ex.: "1:32.456").

      Returns:
          Duração da volta em segundos.

      Raises:
          ValueError: se `raw` não estiver em um formato reconhecido.
      """
  ```
- **Nomenclatura**:
  - Módulos e pacotes: `snake_case` curto e específico (`lap_parser.py`, não
    `utils2.py`).
  - Classes: `PascalCase` (`DriverSession`).
  - Funções, métodos e variáveis: `snake_case` (`get_driver_laps`).
  - Constantes: `UPPER_SNAKE_CASE` (`DEFAULT_TIMEOUT_SECONDS`).
  - Nomes devem descrever o *quê*/*por quê*, não abreviações obscuras (`driver_number`,
    não `drv_no`).
- **Funções pequenas, responsabilidade única.** Se uma função precisa de comentário
  para explicar "o que" ela faz (em vez de "por quê"), ela provavelmente deveria ser
  dividida ou renomeada.
- **Tratamento de exceções**:
  - Nunca use `except:` ou `except Exception:` genérico sem re-lançar ou logar com
    contexto. Capture o tipo específico esperado (`requests.HTTPError`,
    `ValueError`, etc.).
  - Erros de chamadas à API externa (OpenF1) devem ser tratados explicitamente
    (timeout, status HTTP de erro) e nunca vazar como uma exceção genérica sem
    contexto para quem chamou a função — envolva com uma exceção de domínio própria
    quando fizer sentido (ex.: `OpenF1RequestError`).
  - Não use exceções para controle de fluxo normal.
- **Logging**, nunca `print()` em código de produção:
  ```python
  import logging

  logger = logging.getLogger(__name__)
  logger.info("Consultando laps da sessão %s", session_key)
  ```
  Use o nível adequado (`debug`/`info`/`warning`/`error`) e nunca logue segredos
  (tokens, chaves de API) mesmo em `debug`.
- **Configuração e variáveis de ambiente**:
  - Nenhuma credencial, token ou URL sensível é hardcoded no código-fonte.
  - Configuração vem de variáveis de ambiente, centralizadas em um único módulo
    (ex.: `f1/config.py`), nunca lidas com `os.environ` espalhado pelo código.
  - Se for necessário carregar `.env` em desenvolvimento local, adicione
    `python-dotenv` via Poetry (`poetry add python-dotenv`) apenas quando isso for
    de fato necessário — e garanta que `.env` está no `.gitignore` (nunca versionar
    segredos).
- **Segurança**: nunca commitar segredos, tokens ou dados sensíveis; validar/tratar
  qualquer dado vindo de fontes externas (API, arquivo, input do usuário) antes de
  usá-lo; preferir bibliotecas mantidas e atualizadas via Poetry a implementações
  próprias de criptografia/parsing sensível.
- **Compatibilidade**: todo código deve rodar na versão de Python fixada pelo
  projeto (atualmente 3.12). Não use sintaxe de versões mais novas que ainda não
  estão disponíveis nessa versão.

## 8. Ruff (lint, formatação e organização de imports)

Configurado em `pyproject.toml` (`[tool.ruff]`, `[tool.ruff.lint]`,
`[tool.ruff.format]`). Regras ativas: `E` (pycodestyle), `F` (pyflakes), `I`
(organização de imports, isort-like), `UP` (sintaxe moderna), `B` (bugbear), `SIM`
(simplificações).

Comandos obrigatórios antes de finalizar qualquer tarefa:

```bash
poetry run ruff check .              # lint (inclui verificação de imports — regra I)
poetry run ruff check . --fix        # aplica correções automáticas seguras
poetry run ruff format .             # formata o código (substitui black)
poetry run ruff format --check .     # verifica formatação sem alterar arquivos
```

Regras:

- Todo código novo ou alterado deve passar em `ruff check .` e estar formatado por
  `ruff format .` antes de ser considerado pronto.
- **Nunca** silencie um erro com `# noqa` sem um comentário curto explicando o
  motivo técnico real (algo genuinamente inevitável, não conveniência).
- **Nunca** desabilite uma regra em `pyproject.toml` só para fazer um erro pontual
  passar. Se uma regra gera falsos positivos recorrentes e justificáveis, isso é
  uma decisão de configuração a ser discutida, não um `# noqa` a esconder no código.
- O Ruff também formata blocos de código Python dentro de arquivos Markdown do
  projeto (ex.: exemplos em `docs/*.md`) — rode `ruff format .` também depois de
  editar exemplos de código na documentação.

## 9. Testes (pytest)

- Testes ficam em `tests/`, espelhando a estrutura de `src/f1/` (ex.:
  `src/f1/clients/openf1.py` → `tests/clients/test_openf1.py`).
- Convenção de nomes: arquivo `test_<modulo>.py`; função
  `test_<comportamento_esperado>` (ex.: `test_parse_lap_duration_rejeita_formato_invalido`).
- Todo código novo com lógica relevante (parsing, regra de negócio, transformação de
  dados, tratamento de erro) **precisa de teste**. Código trivial (getters,
  `__repr__`, constantes) não precisa de teste dedicado.
- Sempre que uma alteração modificar um comportamento existente, o(s) teste(s)
  correspondente(s) devem ser atualizados no mesmo commit — nunca deixe um teste
  desatualizado "passando por acaso".
- Cubra o caminho feliz **e** os principais casos de borda/erro (entrada inválida,
  vazia, exceção esperada).
- Use fixtures do pytest (`conftest.py`) para setup compartilhado — não duplique
  setup entre testes, não use `unittest.TestCase`.
- **Nunca** faça chamadas de rede reais em teste unitário (ex.: para a OpenF1 API).
  Use mocks/stubs (`unittest.mock`, `pytest-mock` ou respostas gravadas) para isolar
  o código do serviço externo.
- Testes devem ser independentes entre si (qualquer ordem de execução deve produzir
  o mesmo resultado) e não devem depender de detalhes internos de implementação que
  não fazem parte do comportamento sendo testado (evite over-mocking).

Comando para rodar a suíte:

```bash
poetry run pytest
```

## 10. Cobertura de testes (mínimo 50% em `src/f1`)

- A cobertura é medida **apenas sobre `src/f1`** (nunca sobre `tests/`), configurada
  em `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  addopts = "--cov=src/f1 --cov-report=term-missing --cov-fail-under=50"

  [tool.coverage.run]
  source = ["src/f1"]
  ```
- `poetry run pytest` já roda com cobertura por padrão (via `addopts`) e **falha
  automaticamente se a cobertura total cair abaixo de 50%**.
- Para ver apenas o relatório de cobertura com as linhas não cobertas:
  ```bash
  poetry run pytest --cov=src/f1 --cov-report=term-missing
  ```
- Para gerar relatório HTML navegável (útil para investigar lacunas de cobertura):
  ```bash
  poetry run pytest --cov=src/f1 --cov-report=html
  # abrir htmlcov/index.html
  ```
- Antes de finalizar qualquer tarefa que altere `src/f1/`, confirme no relatório
  `term-missing` que as linhas novas/alteradas estão cobertas.
- **Proibido**: remover testes para "fazer a cobertura passar", escrever testes sem
  asserções reais só para tocar linhas, ou reduzir a cobertura total abaixo de 50%
  em qualquer PR/commit.
- Priorize cobrir lógica de negócio e tratamento de erros antes de código trivial.

## 11. Documentação (MkDocs + mkdocstrings)

- Documentação vive em `docs/` (Markdown), configurada em `mkdocs.yml` com o tema
  `material` e o plugin `mkdocstrings` (handler Python, `docstring_style: google`).
- `docs/reference.md` gera documentação de API automaticamente a partir das
  docstrings do pacote (`::: f1`) — por isso toda função/classe pública **deve**
  ter docstring (ver seção 7).
- Rodar a documentação localmente (live reload):
  ```bash
  poetry run mkdocs serve
  ```
- Validar que o site builda sem erros antes de finalizar uma tarefa (use
  `--strict` para transformar avisos de link/nav quebrados em erro):
  ```bash
  poetry run mkdocs build --strict
  ```
- Ao adicionar uma página nova em `docs/`, registre-a em `mkdocs.yml` (`nav`) — uma
  página que só existe como arquivo, sem estar na navegação, é considerada
  incompleta.
- Sempre que uma alteração:
  - adicionar uma funcionalidade pública relevante,
  - mudar um comportamento existente,
  - alterar configuração, instalação ou forma de uso do projeto,

  a documentação correspondente em `docs/` deve ser criada/atualizada no mesmo
  commit/PR.
- `README.md` deve conter apenas uma introdução curta e links para `SKILL.md` e para
  a documentação completa — não duplicar conteúdo extenso do MkDocs ali.

## 12. Fluxo obrigatório para qualquer alteração

Toda tarefa neste projeto segue este fluxo, nesta ordem:

1. Analisar a estrutura atual do projeto antes de modificar qualquer arquivo.
2. Identificar as convenções e padrões já utilizados (nomes, organização de
   módulos, estilo de teste já existente).
3. Verificar as configurações existentes de Poetry, pyenv, Ruff, pytest e MkDocs
   em `pyproject.toml` / `mkdocs.yml` / `.python-version` — não presumir.
4. Reutilizar estruturas e componentes já existentes quando fizer sentido.
5. Implementar a alteração respeitando a arquitetura modular do projeto (seção 4).
6. Criar ou atualizar os testes necessários (seção 9).
7. Rodar `poetry run pytest` e garantir cobertura mínima de 50% em `src/f1`
   (seção 10).
8. Rodar `poetry run ruff check .` e `poetry run ruff format .` (seção 8).
9. Rodar os testes novamente após qualquer correção de lint/formatação.
10. Verificar se a documentação precisa de atualização e atualizá-la (seção 11).
11. Rodar `poetry run mkdocs build --strict` para validar que a documentação
    continua buildando.
12. Ao finalizar, informar claramente: quais arquivos foram alterados, quais
    validações foram executadas (ruff check, ruff format, pytest+cobertura, mkdocs
    build) e se todas passaram — sem essa informação a tarefa não está concluída.

## 13. Checklist obrigatório antes de finalizar uma tarefa

- [ ] Analisei a estrutura e as convenções existentes antes de implementar.
- [ ] Reutilizei componentes/estruturas existentes em vez de duplicar.
- [ ] O código novo está em `src/f1/`, no módulo/camada correta (seção 4).
- [ ] Funções e métodos públicos têm type hints e docstrings (estilo Google).
- [ ] Erros são tratados explicitamente; nenhum `except Exception` genérico sem
      contexto; nenhum segredo hardcoded ou logado.
- [ ] `poetry run ruff check .` passa sem erros (nenhum `# noqa` injustificado).
- [ ] `poetry run ruff format --check .` passa sem alterações pendentes.
- [ ] Testes novos/atualizados cobrem caminho feliz e casos de borda relevantes.
- [ ] `poetry run pytest` passa e a cobertura de `src/f1` está ≥ 50%.
- [ ] Nenhum teste foi removido ou esvaziado apenas para atingir a cobertura.
- [ ] Documentação em `docs/` (e `mkdocs.yml` nav) atualizada, se aplicável.
- [ ] `poetry run mkdocs build --strict` builda sem erros.
- [ ] `pyproject.toml`/`poetry.lock` atualizados juntos, se dependências mudaram.
- [ ] Resumo final informa arquivos alterados e resultado de cada validação.

## 14. Comandos úteis (referência rápida)

```bash
# Ambiente
pyenv install --skip-existing $(cat .python-version)
poetry env use $(cat .python-version)
poetry install
poetry shell

# Dependências
poetry add <pacote>
poetry add --group dev <pacote>
poetry remove [--group dev] <pacote>
poetry lock

# Lint e formatação
poetry run ruff check .
poetry run ruff check . --fix
poetry run ruff format .
poetry run ruff format --check .

# Testes e cobertura
poetry run pytest
poetry run pytest --cov=src/f1 --cov-report=term-missing
poetry run pytest --cov=src/f1 --cov-report=html

# Documentação
poetry run mkdocs serve
poetry run mkdocs build --strict
```

### Atalhos (Taskipy — `[tool.taskipy.tasks]` em `pyproject.toml`)

Equivalentes aos comandos de lint/testes/docs acima, para digitar menos no dia a
dia. Não substituem os comandos originais como critério de "pronto" (seção 13) —
são apenas atalhos para os mesmos comandos:

```bash
poetry run task test          # equivale a: poetry run pytest
poetry run task lint          # equivale a: poetry run ruff check .
poetry run task format        # equivale a: poetry run ruff format .
poetry run task format-check  # equivale a: poetry run ruff format --check .
poetry run task docs          # equivale a: poetry run mkdocs build --strict
poetry run task docs-serve    # equivale a: poetry run mkdocs serve
poetry run task dashboard     # equivale a: poetry run streamlit run dashboard/app.py
```

## 16. Integração contínua (GitHub Actions)

- Workflow em `.github/workflows/ci.yml`, disparado em `push` e `pull_request`
  para as branches `main` e `dev`.
- Roda, nesta ordem, sobre a versão de Python fixada em `.python-version`:
  `poetry install --with dev`, `poetry run task lint`,
  `poetry run task format-check`, `poetry run task test` (com a cobertura
  mínima de 50%, seção 10) e `poetry run task docs` (build `--strict`).
- Qualquer alteração que quebre lint, formatação, testes/cobertura ou o build
  da documentação falha a CI — corrija localmente com os mesmos comandos antes
  de abrir/atualizar um PR.
- Ao adicionar uma dependência necessária apenas para lint/testes/docs, ela vai
  no grupo `dev` (seção 6), já instalado pela CI; grupos `notebooks` e
  `dashboard` não são instalados na CI (nenhum teste depende deles).

## 15. Regras que a IA deve seguir (resumo — não negociável)

- Nunca usar `pip` para instalar, remover ou atualizar dependências — sempre Poetry.
- Nunca criar ou ativar uma venv fora da gerenciada pelo Poetry.
- Nunca ignorar a versão do Python definida em `.python-version`/`pyproject.toml`.
- Nunca adicionar uma dependência sem necessidade real, nem duplicar uma já
  existente.
- Nunca duplicar funcionalidade já implementada no projeto.
- Nunca alterar configurações existentes (Ruff, pytest, Poetry, MkDocs) sem
  entender seu propósito atual e sem justificativa para a mudança.
- Nunca remover ou esvaziar testes para forçar a cobertura mínima.
- Nunca reduzir a cobertura de `src/f1` abaixo de 50%.
- Nunca desabilitar uma regra do Ruff ou usar `# noqa` só para o lint passar, sem
  justificativa técnica real.
- Nunca implementar uma funcionalidade relevante sem considerar teste e
  documentação correspondentes.
- Nunca inventar um padrão, estrutura ou configuração sem antes verificar o que já
  existe no projeto.
- Sempre que uma nova implementação conflitar com a arquitetura existente, analisar
  o impacto e decidir de forma explícita (documentando o motivo) antes de prosseguir
  — não simplesmente contornar o conflito.
- Sempre priorizar simplicidade, clareza e manutenibilidade em vez de soluções
  complexas ou "espertas".
- Sempre finalizar a tarefa informando arquivos alterados e resultado de todas as
  validações executadas (seção 12, item 12).
