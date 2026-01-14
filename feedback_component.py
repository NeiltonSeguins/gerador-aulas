import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def feedback_sidebar():
    with st.sidebar:
        st.divider()
        st.header("🗣️ Feedback")
        
        with st.expander("Avalie o App"):
            with st.form("feedback_form"):
                tipo = st.selectbox("Tipo:", ["Sugestão", "Elogio", "Bug/Erro"])
                nota = st.slider("Nota:", 1, 5, 5)
                comentario = st.text_area("Mensagem")
                
                enviar = st.form_submit_button("Enviar")
                
                if enviar:
                    if not comentario:
                        st.warning("Escreva uma mensagem.")
                    else:
                        salvar_no_sheets(tipo, nota, comentario)

def salvar_no_sheets(tipo, nota, comentario):
    try:
        # Acessa os segredos do TOML
        # Precisamos converter o objeto do toml de volta para dict compatível com JSON
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # Define o escopo
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Autentica
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha pelo NOME (Tem que ser exato)
        sheet = client.open("feedback_app_aulas").sheet1
        
        # Pega dados do usuário
        usuario = st.session_state.get("username", "Anônimo")
        data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Adiciona a linha
        sheet.append_row([data_hora, usuario, tipo, nota, comentario])
        
        st.success("Obrigado! Seu feedback foi salvo.")
        
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")