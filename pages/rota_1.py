import streamlit as st

st.set_page_config(page_title="Página de Teste 1")

# --- BLOQUEIO DE SEGURANÇA ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Por favor, faça login na página principal primeiro.")
    st.stop() # Para a execução aqui
# -----------------------------

st.title("🧪 Página de Teste 1")
st.write("Esta é uma rota secundária apenas para testar navegação.")
st.write("Aqui você poderia colocar uma ferramenta de gerar atividades, por exemplo.")