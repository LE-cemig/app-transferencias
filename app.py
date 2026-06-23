import streamlit as st
import pandas as pd
import os

# Configuração
st.set_page_config(
    page_title="Transferência de Materiais",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Esconder menu
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Título (sem emoji)
st.title("Solicitação de Transferência")

# Depósitos
dep_origem = st.text_input("Depósito de origem")
dep_destino = st.text_input("Depósito de destino")

# Texto sem emoji
st.markdown("Itens da transferência (pode colar do Excel)")

# Tabela
df = st.data_editor(
    pd.DataFrame({
        "material": [""],
        "quantidade": [""],
        "unidade": [""]
    }),
    num_rows="dynamic",
    use_container_width=True
)

# Botão
if st.button("Enviar"):

    erros = False

    if dep_origem.strip() == "" or dep_destino.strip() == "":
        st.error("Preencha os depósitos")
        erros = True

    df = df[df["material"].astype(str).str.strip() != ""]

    if df["material"].duplicated().any():
        st.error("Material duplicado")
        erros = True

    if not erros:

        if os.path.exists("dados.csv"):
            base = pd.read_csv("dados.csv")
        else:
            base = pd.DataFrame()

        df["dep_origem"] = dep_origem
        df["dep_destino"] = dep_destino
        df["status"] = "pendente"
        df["reserva"] = ""

        base = pd.concat([base, df], ignore_index=True)
        base.to_csv("dados.csv", index=False)

        st.success("Enviado com sucesso")
