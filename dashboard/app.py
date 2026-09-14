"""Dashboard Streamlit: voltas mais rápidas por circuito, por temporada.

Executar com:
    poetry run streamlit run dashboard/app.py

Este arquivo é apenas a camada de apresentação: toda a lógica de extração e
ranking vem de `f1.pipelines.fastest_laps` (testada em
`tests/pipelines/test_fastest_laps.py`). Por isso, assim como o notebook em
`notebooks/`, fica fora de `src/f1/` e da cobertura obrigatória de testes.
"""

import streamlit as st

from f1.clients.exceptions import OpenF1RequestError
from f1.pipelines.fastest_laps import (
    DEFAULT_TOP_N,
    CircuitFastestLaps,
    iter_fastest_laps_by_circuit,
)

st.set_page_config(page_title="F1 — Voltas mais rápidas por circuito", layout="wide")
st.title("Voltas mais rápidas por circuito")
st.caption("Dados extraídos em tempo real da OpenF1 API (https://openf1.org).")


def _render_circuit(circuit: CircuitFastestLaps) -> None:
    """Renderiza a tabela de voltas mais rápidas de um circuito."""
    st.subheader(f"{circuit.circuit_short_name} — {circuit.country_name}")
    st.table(
        [
            {
                "Posição": posicao,
                "Piloto": lap.driver_name,
                "Volta": lap.lap_number,
                "Tempo (s)": lap.lap_duration,
            }
            for posicao, lap in enumerate(circuit.fastest_laps, start=1)
        ]
    )


with st.sidebar:
    year = st.number_input(
        "Temporada", min_value=2018, max_value=2100, value=2023, step=1
    )
    session_type = st.selectbox(
        "Tipo de sessão", ["Race", "Qualifying", "Sprint"], index=0
    )
    top_n = st.slider(
        "Voltas por circuito", min_value=1, max_value=10, value=DEFAULT_TOP_N
    )
    buscar = st.button("Buscar dados", type="primary")

query_key = (int(year), top_n, session_type)
consulta_pendente = buscar and st.session_state.get("query_key") != query_key

if consulta_pendente:
    st.session_state["query_key"] = query_key
    st.session_state["circuits"] = []
    st.session_state["error"] = None

    progresso = st.empty()
    try:
        for circuit in iter_fastest_laps_by_circuit(*query_key):
            st.session_state["circuits"].append(circuit)
            progresso.caption(
                f"{len(st.session_state['circuits'])} circuito(s) carregado(s) "
                "até agora — a tabela de cada um aparece assim que fica pronta."
            )
            _render_circuit(circuit)
    except OpenF1RequestError as exc:
        st.session_state["error"] = str(exc)
    progresso.empty()
elif st.session_state.get("query_key") == query_key:
    for circuit in st.session_state.get("circuits", []):
        _render_circuit(circuit)

carregado = st.session_state.get("query_key") == query_key

if st.session_state.get("error"):
    st.error(f"Erro ao consultar a OpenF1 API: {st.session_state['error']}")
elif not carregado:
    st.info("Escolha a temporada na barra lateral e clique em **Buscar dados**.")
elif not st.session_state.get("circuits"):
    st.info("Nenhum dado encontrado para os filtros selecionados.")
