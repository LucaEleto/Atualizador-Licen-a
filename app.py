import streamlit as st
import pandas as pd
import mysql.connector

# Função de conexão
def conectar_banco():
    return mysql.connector.connect(
        host='162.241.203.62',
        database='avinfo61_licencas',
        user='avinfo61_servico',
        password='Sclara02'
    )

st.image('logonova.bmp', width=100)
st.title('Atualizar de Licença')

# Inicializar session_state para armazenar DataFrame
if 'df_original' not in st.session_state:
    st.session_state.df_original = None

# Entrada de busca
busca = st.text_input('Pesquisar Cliente (nome ou fantasia)')

# Botão de busca
if st.button('Buscar'):
    con = conectar_banco()
    cursor = con.cursor()
    consulta = """
        SELECT cliente, fantasia, dias, vencimento 
        FROM licencas_clientes 
        WHERE cliente LIKE %s OR fantasia LIKE %s
        ORDER BY cliente
    """
    cursor.execute(consulta, (f"%{busca}%", f"%{busca}%"))
    resultados = cursor.fetchall()
    cursor.close()
    con.close()

    if resultados:
        df = pd.DataFrame(resultados, columns=['Cliente', 'Fantasia', 'Dias', 'Vencimento'])
        st.session_state.df_original = df  # salva na sessão
    else:
        st.warning("Nenhum cliente encontrado.")
        st.session_state.df_original = None  # limpa

# Mostrar editor se houver dados
if st.session_state.df_original is not None:
    st.subheader('Editar Dias')
    df_editado = st.data_editor(
        st.session_state.df_original,
        num_rows="dynamic",
        use_container_width=True,
        key='editor'
    )

    # Botão para salvar
    if st.button('Salvar Alterações'):
        con = conectar_banco()
        cursor = con.cursor()
        linhas_afetadas = 0

        for index, row in df_editado.iterrows():
            cliente = row['Cliente']
            dias_novo = row['Dias']
            try:
                cursor.execute(
                    "UPDATE licencas_clientes SET dias = %s WHERE cliente = %s",
                    (dias_novo, cliente)
                )
                if cursor.rowcount > 0:
                    linhas_afetadas += 1
            except Exception as e:
                st.error(f"Erro ao atualizar cliente {cliente}: {e}")
                
        for index, row in df_editado.iterrows():
            cliente = row['Cliente']
            vencimento_novo = row['Vencimento']
            try:
                cursor.execute(
                    "UPDATE licencas_clientes SET vencimento = %s WHERE cliente = %s",
                    (vencimento_novo, cliente)
                )
                if cursor.rowcount > 0:
                    linhas_afetadas += 1
            except Exception as e:
                st.error(f'Erro ao atualizar cliente {cliente}: {e}')
                
        con.commit()
        cursor.close()
        con.close()

        if linhas_afetadas > 0:
            st.success(f"{linhas_afetadas} registro(s) atualizado(s) com sucesso!")
        else:
            st.info("Nenhuma alteração detectada ou salva.")
