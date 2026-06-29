import streamlit as st
import pandas as pd
from datetime import datetime

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Transferência", layout="wide")

# ========================
# BASE DE MATERIAIS (REDE)
# ========================
@st.cache_data
def carregar_materiais():
    caminho = r"\\Sacorparq1\GROUPS\SA\EMLE\EMLE-PJ-Obras-EMLE\EM-LE\Materiais\Base de dados codigo\Materiais e descrições resumidos.xlsx"
    df = pd.read_excel(caminho)
    return df

materiais_df = carregar_materiais()

# ========================
# BUSCAR MATERIAL
# ========================
def buscar_material(codigo):
    linha = materiais_df[materiais_df["Material"] == codigo]

    if not linha.empty:
        return (
            linha.iloc[0]["Texto breve material"],
            linha.iloc[0]["UMB"]
        )
    return "", ""

# ========================
# LOGIN
# ========================
if "login_ok" not in st.session_state:
    st.session_state.login_ok = False

if not st.session_state.login_ok:
    st.title("Login")

    nome = st.text_input("Nome")
    matricula = st.text_input("Matrícula")

    if st.button("Entrar"):
        if nome and matricula:
            st.session_state.login_ok = True
            st.session_state.nome = nome
            st.session_state.matricula = matricula
            st.rerun()
        else:
            st.error("Preencha todos os dados")

    st.stop()

# ========================
# TELA PRINCIPAL
# ========================
st.title("Solicitação de Transferência")

st.write(f"Usuário: {st.session_state.nome} | Matrícula: {st.session_state.matricula}")

dep_origem = st.text_input("Depósito de origem")
dep_destino = st.text_input("Depósito de destino")

opcoes_lote = ["NOVO", "RECUPERÁVEL", "REFORMADO", "REINCORPORADO", "SUCATA"]

# tabela
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "material": [""],
        "descricao": [""],
        "unidade": [""],
        "quantidade": [""],
        "lote": ["NOVO"],
        "observacao": [""]
    })

df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    column_config={
        "lote": st.column_config.SelectboxColumn(
            "Lote",
            options=opcoes_lote
        )
    }
)

# ========================
# AUTO-PREENCHIMENTO
# ========================
for i, row in df.iterrows():
    try:
        codigo = int(float(row["material"]))
        desc, umb = buscar_material(codigo)

        df.at[i, "descricao"] = desc
        df.at[i, "unidade"] = umb
    except:
        continue

st.session_state.df = df

# ========================
# ENVIO (SALVAR NA REDE)
# ========================
if st.button("Enviar"):

    erros = False

    # validar depósitos
    if not dep_origem or not dep_destino:
        st.error("Preencha os depósitos")
        erros = True

    # remover linhas vazias
    df = df[df["material"].notna()]
    df = df[df["material"].astype(str).str.strip() != ""]

    # validar duplicidade
    if df.duplicated(subset=["material", "lote"]).any():
        st.error("Material duplicado com mesmo lote")
        erros = True

    if not erros:
        try:
            # adicionar dados extras
            df["dep_origem"] = dep_origem
            df["dep_destino"] = dep_destino
            df["nome"] = st.session_state.nome
            df["matricula"] = st.session_state.matricula
            df["data"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            df["status"] = "pendente"

            # ✅ CAMINHO NA REDE
            arquivo = r"\\Sacorparq1\GROUPS\SA\EMLE\EMLE-PJ-Obras-EMLE\EM-LE\Materiais\Base de dados codigo\transferencias.xlsx"

            # tentar ler arquivo existente
            try:
                base = pd.read_excel(arquivo)
            except:
                base = pd.DataFrame()

            # adicionar novos dados
            base = pd.concat([base, df], ignore_index=True)

            # salvar
            base.to_excel(arquivo, index=False)

            st.success("Enviado com sucesso ✅ (salvo na rede)")

            # limpar tabela
            st.session_state.df = pd.DataFrame({
                "material": [""],
                "descricao": [""],
                "unidade": [""],
                "quantidade": [""],
                "lote": ["NOVO"],
                "observacao": [""]
            })

        except Exception as e:
            st.error(f"Erro ao salvar na rede: {e}")
