import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Cadastro de Equipamentos Técnicos", layout="wide")

TIPOS_EQUIPAMENTOS = {
    "Ventiladores e exaustores": ["marca", "modelo", "descrição", "data_cadastro", "observações"],
    "Split System": ["marca", "modelo", "descrição", "capacidade_frigorifica", "data_cadastro", "observações"],
    "Fancoletes hidronicos": ["marca", "modelo", "descrição", "capacidade_frigorifica", "data_cadastro", "observações"],
    "Fancoletes hospitalares": ["marca", "modelo", "descrição", "capacidade_frigorifica", "data_cadastro", "observações"],
    "Fancoil/UTA/AHU": ["marca", "modelo", "descrição", "capacidade_frigorifica", "data_cadastro", "observações"],
    "Cortina de ar": ["marca", "modelo", "tamanho", "descrição", "data_cadastro", "observações"],
    "Coifa": ["marca", "modelo", "tamanho", "descrição", "data_cadastro", "observações"]
}

def conectar():
    return sqlite3.connect("equipamentos.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    for tipo, campos in TIPOS_EQUIPAMENTOS.items():
        campos_sql = ", ".join([f"{campo} TEXT" if 'data' not in campo else f"{campo} DATE" for campo in campos])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS '{tipo}' (id INTEGER PRIMARY KEY AUTOINCREMENT, {campos_sql})")
    conn.commit()
    conn.close()

def inserir_dados(tipo, dados):
    try:
        conn = conectar()
        cursor = conn.cursor()
        campos = TIPOS_EQUIPAMENTOS[tipo]
        placeholders = ", ".join(["?"] * len(campos))
        cursor.execute(f"INSERT INTO '{tipo}' ({', '.join(campos)}) VALUES ({placeholders})", dados)
        conn.commit()
        st.success("Equipamento cadastrado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
    finally:
        conn.close()

def consultar_dados(tipo):
    conn = conectar()
    df = pd.read_sql_query(f"SELECT * FROM '{tipo}'", conn)
    conn.close()
    return df

def excluir_dado(tipo, id_registro):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM '{tipo}' WHERE id=?", (id_registro,))
        conn.commit()
        st.success("Registro excluído com sucesso!")
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")
    finally:
        conn.close()

def exportar_para_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer

def interface_tipo(tipo):
    st.header(f"Cadastro - {tipo}")
    campos = TIPOS_EQUIPAMENTOS[tipo]
    dados = []
    with st.form(f"form_{tipo}"):
        for campo in campos:
            if campo == "data_cadastro":
                valor = st.date_input("Data de Cadastro", value=datetime.today(), key=f"{campo}_{tipo}")
            else:
                valor = st.text_input(campo.capitalize(), key=f"{campo}_{tipo}")
            dados.append(str(valor))
        submitted = st.form_submit_button("Salvar")
        if submitted:
            inserir_dados(tipo, dados)

    df = consultar_dados(tipo)

    st.subheader("Registros cadastrados")
    filtro = st.text_input("Filtro de busca", key=f"filtro_{tipo}")
    if filtro:
        df_filtrado = df[df.apply(lambda row: row.astype(str).str.contains(filtro, case=False).any(), axis=1)]
    else:
        df_filtrado = df
    st.dataframe(df_filtrado, use_container_width=True)

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Exportar para Excel", key=f"exportar_{tipo}"):
            buffer = exportar_para_excel(df_filtrado)
            st.download_button("Baixar Excel", data=buffer, file_name=f"{tipo}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col2:
        id_excluir = st.number_input("ID do registro para excluir", min_value=1, step=1, key=f"excluir_{tipo}")
        if st.button("Excluir", key=f"btn_excluir_{tipo}"):
            excluir_dado(tipo, id_excluir)

criar_tabelas()
tabs = st.tabs(list(TIPOS_EQUIPAMENTOS.keys()))
for i, tipo in enumerate(TIPOS_EQUIPAMENTOS.keys()):
    with tabs[i]:
        interface_tipo(tipo)