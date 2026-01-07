import streamlit as st
import pandas as pd # Se não tiver pandas instalado, rode pip install pandas

st.set_page_config(page_title="Dash Teste")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Acesso Negado.")
    st.stop()

st.title("📊 Outra Ferramenta de Teste")
st.write("Simulando uma página com dados.")

data = {'Alunos': [10, 20, 30, 40], 'Notas': [5, 7, 8, 6]}
st.bar_chart(data)