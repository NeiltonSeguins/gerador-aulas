import streamlit as st
import time
from google import genai
from markdown import markdown
import db 

# --- NOVA BIBLIOTECA DE PDF ---
from xhtml2pdf import pisa

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Portal do Professor", page_icon="🎓")

db.init_db()

# --- CSS PARA ESTILIZAR O PDF (AQUI É O SEGREDO) ---
# Aqui definimos como o PDF vai se parecer.
PDF_STYLE = """
<style>
    @page {
        size: a4 portrait;
        margin: 2cm;
    }
    body {
        font-family: Helvetica, sans-serif;
        font-size: 12pt;
        line-height: 1.5;
        color: #000000;
    }
    h1 {
        font-size: 18pt;
        color: #000000;
        margin-top: 30px;
        margin-bottom: 15px;
        text-transform: uppercase;
        border-bottom: 1px solid #000000;
        padding-bottom: 5px;
    }
    h2 {
        font-size: 14pt;
        color: #000000;
        margin-top: 25px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    h3 {
        font-size: 12pt;
        font-weight: bold;
        margin-top: 15px;
    }
    p {
        margin-bottom: 10px;
        text-align: justify;
    }
    ul, ol {
        margin-bottom: 15px;
        margin-left: 20px;
    }
    li {
        margin-bottom: 5px;
    }
    /* ESTILIZAÇÃO DE TABELAS */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    th, td {
        border: 1px solid #000000;
        padding: 8px;
        text-align: left;
        font-size: 10pt;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    hr {
        color: #000000;
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
"""

# --- FUNÇÃO GERADORA DE PDF (XHTML2PDF) ---
def create_pdf(markdown_content):
    # 1. Converte Markdown para HTML
    # A extensão 'tables' é OBRIGATÓRIA para tabelas funcionarem
    html_body = markdown(markdown_content, extensions=['tables', 'fenced_code'])
    
    # 2. Monta o HTML completo com o CSS
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        {PDF_STYLE}
    </head>
    <body>
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>Plano de Aula</h1>
            <p style="font-size: 10pt; color: #666;">Gerado por IA</p>
        </div>
        {html_body}
    </body>
    </html>
    """
    
    # 3. Gera o PDF
    output_filename = "plano_aula.pdf"
    with open(output_filename, "wb") as result_file:
        pisa_status = pisa.CreatePDF(
            src=full_html,     # HTML de entrada
            dest=result_file   # Arquivo de saída
        )
    
    if pisa_status.err:
        raise Exception("Erro ao gerar PDF")
        
    return output_filename

# --- LOGIN ---
def login_screen():
    st.title("🔐 Acesso ao Sistema")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary"):
            if db.check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Bem-vindo!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Dados incorretos")
        st.info("Teste: admin / 123")

# --- APP PRINCIPAL ---
def main_app():
    # Sidebar e Logout
    with st.sidebar:
        st.write(f"Olá, **{st.session_state.username}**")
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.rerun()

    st.title("📚 Planejador de Aulas")

    # API Key
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        st.error("Configure o secrets.toml!")
        return

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        tema = st.text_input("Tema da Aula")
        disciplina = st.text_input("Disciplina")
    with col2:
        turma = st.selectbox("Turma", ["Fundamental 1", "Fundamental 2", "Médio"])
        tempo = st.number_input("Duração (min)", value=45, step=5)
    
    objetivo = st.text_area("Objetivo")

    # Estado
    if "plano_gerado" not in st.session_state:
        st.session_state.plano_gerado = ""

    # Botão Gerar
    if st.button("Gerar Plano", type="primary"):
        if not tema or not disciplina:
            st.warning("Preencha Tema e Disciplina")
        else:
            with st.spinner('Criando plano e tabelas...'):
                try:
                    client = genai.Client(api_key=api_key)
                    # Prompt Refinado para Tabelas
                    prompt = f"""
                    Crie um plano de aula sobre {tema} ({disciplina}, {turma}, {tempo}min).
                    Objetivo: {objetivo}.
                    
                    IMPORTANTE:
                    1. Use Markdown padrão.
                    2. SE PRECISAR LISTAR HORÁRIOS OU MATERIAIS, USE TABELAS MARKDOWN (Sintaxe | Coluna |).
                    3. Seja estruturado (Introdução, Desenvolvimento, Avaliação).
                    """
                    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
                    st.session_state.plano_gerado = response.text
                except Exception as e:
                    st.error(f"Erro na IA: {e}")

    # Exibição e Download
    if st.session_state.plano_gerado:
        st.markdown("---")
        st.markdown(st.session_state.plano_gerado)
        
        try:
            # Chama a nova função xhtml2pdf
            pdf_file = create_pdf(st.session_state.plano_gerado)
            
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📄 Baixar PDF Profissional",
                    data=f.read(),
                    file_name=f"plano_{tema.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

# --- CONTROLE DE ROTAS ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    login_screen()