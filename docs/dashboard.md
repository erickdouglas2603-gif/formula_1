# Dashboard: voltas mais rápidas por circuito

## Pipeline (`f1.pipelines.fastest_laps`)

`iter_fastest_laps_by_circuit` percorre todos os fins de semana de Grande
Prêmio (`meetings`) de uma temporada, localiza a sessão do tipo pedido em cada
um (por padrão, a corrida) e **gera** as voltas mais rápidas dessa sessão, já
com o nome do piloto resolvido — um circuito por vez, assim que fica pronto,
sem esperar a temporada inteira:

```python
from f1.pipelines.fastest_laps import iter_fastest_laps_by_circuit

for circuit in iter_fastest_laps_by_circuit(year=2023, top_n=5):
    print(circuit.circuit_short_name, circuit.country_name)
    for lap in circuit.fastest_laps:
        print(f"  {lap.driver_name}: volta {lap.lap_number} em {lap.lap_duration}s")
```

Se preferir o resultado completo de uma vez (ex.: um script que só imprime no
final), `build_fastest_laps_by_circuit` consome o gerador inteiro em uma
lista:

```python
from f1.pipelines.fastest_laps import build_fastest_laps_by_circuit

circuits = build_fastest_laps_by_circuit(year=2023, top_n=5)  # list[CircuitFastestLaps]
```

- Circuitos sem sessão do tipo pedido (ex.: eventos de teste de pré-temporada)
  são ignorados.
- Voltas sem `lap_duration` (ex.: incompletas) e voltas de saída do pit lane
  (`is_pit_out_lap=True`) são descartadas antes do ranking.
- `session_type` aceita qualquer valor retornado pela OpenF1 API para esse
  campo (`"Race"`, `"Qualifying"`, `"Sprint"`, ...).
- `client` pode receber um `f1.clients.openf1.OpenF1Client` já configurado —
  ver [Configuração e Cliente](client.md).

## Dashboard (Streamlit)

O dashboard em `dashboard/app.py` é uma camada de apresentação sobre o pipeline
acima: escolhe a temporada, o tipo de sessão e quantas voltas mostrar por
circuito, e exibe uma tabela por circuito **assim que cada uma fica pronta**
(consumindo `iter_fastest_laps_by_circuit` diretamente), em vez de bloquear a
tela por 1-2 minutos até a temporada inteira ser consultada. Os resultados
ficam guardados em `st.session_state` enquanto os filtros não mudam, para não
refazer a consulta a cada interação com a página. Fica fora de `src/f1/`
(como `notebooks/`) e não entra na cobertura obrigatória de testes — a lógica
que ele usa é testada em `tests/pipelines/test_fastest_laps.py`.

Rodar localmente:

```bash
poetry run poe dashboard
# equivale a: poetry run streamlit run dashboard/app.py
```

Abre em `http://localhost:8501`.

::: f1.pipelines.fastest_laps
