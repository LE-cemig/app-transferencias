import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Transferência de Materiais", layout="wide")

st.title("📦 Solicitação de Transferência")

# Depósitos
dep_origem = st.text_input("Depósito de origem")
dep_destino = st.text_input("Depósito de destino")

st.markdown("### Itens da transferência (pode colar do Excel 👇)")

# tabela editável (pode colar do Excel)
df = st.data_editor(
    pd.DataFrame({
        "material": [""],
        "quantidade": [""],
        "unidade": [""]
    }),
    num_rows="dynamic",
    use_container_width=True
)

# botão enviar
if st.button("✅ Enviar solicitação"):

    erros = False

    # validação simples
    if dep_origem == "" or dep_destino == "":
        st.error("Preencha os depósitos!")
        erros = True

    # remover linhas vazias
    df = df[df["material"] != ""]

    # verificar duplicado
    if df["material"].duplicated().any():
        st.error("Material duplicado na solicitação!")
        erros = True

    if not erros:

        # criar arquivo se não existir
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

        st.success("✅ Solicitação enviada com sucesso!")
        st.write(df)
