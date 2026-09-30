import pandas as pd
import streamlit as st

from config import ID, NOMES_AMIGAVEIS
from priorizar import carregar_modelo, priorizar

CORES = {"Alta": "#c0392b", "Média": "#e67e22", "Baixa": "#27ae60"}

st.set_page_config(page_title="Painel de Prioridades", layout="wide")
st.title("Painel de Prioridades")
st.caption("Envie a planilha de casos abertos. O painel indica quais merecem "
           "atenção primeiro. A decisão final continua sendo da equipe.")

pacote = carregar_modelo()

arquivo = st.file_uploader("Planilha de casos abertos (CSV)", type="csv")
if arquivo is None:
    st.info("Aguardando a planilha. Para testar, use dados/casos_abertos_simulado.csv.")
    st.stop()  # sem planilha não tem o que mostrar, para aqui

lista = priorizar(pd.read_csv(arquivo), pacote)

# contadores no topo
col1, col2, col3 = st.columns(3)
col1.metric("Prioridade alta", (lista["prioridade"] == "Alta").sum())
col2.metric("Prioridade média", (lista["prioridade"] == "Média").sum())
col3.metric("Prioridade baixa", (lista["prioridade"] == "Baixa").sum())

# por padrão esconde as baixas, para a tela não ficar poluída
mostrar = st.multiselect("Mostrar", ["Alta", "Média", "Baixa"], default=["Alta", "Média"])
visivel = lista[lista["prioridade"].isin(mostrar)]

tabela = pd.DataFrame({
    "Caso": visivel[ID],
    "Prioridade": visivel["prioridade"],
    "Chance estimada": (visivel["probabilidade"] * 100).round().astype(int).astype(str) + "%",
    "Por que está aqui": visivel["por_que"],
})


def pintar(valor):
    # pinta só a célula da coluna Prioridade com a cor da faixa
    if valor in CORES:
        return f"background-color: {CORES[valor]}; color: white"
    return ""


st.dataframe(tabela.style.map(pintar, subset=["Prioridade"]), width="stretch", hide_index=True)

st.download_button("Baixar lista priorizada", lista.to_csv(index=False).encode("utf-8"),
                   "lista_priorizada.csv", "text/csv")

with st.expander("Como o painel chega nesse resultado"):
    st.write(f"Modelo em uso: **{pacote['nome']}**, treinado com o histórico da organização. "
             "Os sinais considerados são: " + ", ".join(NOMES_AMIGAVEIS.values())
             + ", categoria e canal de atendimento.")
