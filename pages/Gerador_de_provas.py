import streamlit as st
import re  # Importação necessária para corrigir as alternativas
from google import genai
from markdown import markdown
from xhtml2pdf import pisa

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Avaliações", page_icon="📝")

# --- VERIFICAÇÃO DE LOGIN ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Por favor, faça login na página principal primeiro.")
    st.stop()

# --- CSS / ESTILO DO PDF ---
PDF_STYLE = """
<style>
    @page { size: a4 portrait; margin: 2cm; }
    body { font-family: Helvetica, sans-serif; font-size: 12pt; color: #000; }
    h1 { font-size: 16pt; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; text-transform: uppercase; text-align: center; }
    h2 { font-size: 13pt; margin-top: 25px; margin-bottom: 10px; font-weight: bold; background-color: #eee; padding: 5px; border-left: 5px solid #333; }
    p { text-align: justify; line-height: 1.5; margin-bottom: 8px; }
    
    /* Força as alternativas a terem espaço entre elas */
    li { margin-bottom: 8px; list-style-type: none; }
    ul { margin-top: 5px; padding-left: 0; }
    
    .gabarito { border: 1px dashed #000; padding: 15px; margin-top: 40px; page-break-before: always; }
</style>
"""

# --- FUNÇÃO DE CORREÇÃO DE TEXTO (REGEX) ---
def format_alternatives_vertical(text):
    """
    Função 'Força Bruta' que procura padrões como ' A) texto B) texto'
    e insere quebras de linha antes das letras B, C, D, E.
    """
    # Passo 1: Se a IA colocou A) B) C) na mesma linha, quebra antes das letras
    # O regex procura espaços seguidos de uma letra maiúscula e parenteses: \s([B-E]\))
    text = re.sub(r'\s+([A-E]\))', r'\n\n\1', text)
    
    # Passo 2: Garante que haja espaço antes das questões numeradas (1., 2.)
    text = re.sub(r'\n(\d+\.)', r'\n\n\1', text)
    
    return text

# --- FUNÇÃO GERADORA DE PDF ---
def create_assessment_pdf(html_content):
    full_html = f"""
    <html>
    <head><meta charset="utf-8">{PDF_STYLE}</head>
    <body>
        {html_content}
    </body>
    </html>
    """
    output_filename = "avaliacao.pdf"
    with open(output_filename, "wb") as result_file:
        pisa_status = pisa.CreatePDF(src=full_html, dest=result_file)
    if pisa_status.err:
        raise Exception("Erro ao gerar PDF")
    return output_filename

# --- INTERFACE ---
st.title("📝 Gerador de Avaliações")
st.markdown("Crie provas personalizadas, formatadas e inclusivas.")

# 1. Configurações Principais
col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("Tema da Avaliação", placeholder="Ex: Ecossistemas Brasileiros")
    disciplina = st.text_input("Disciplina", placeholder="Ex: Geografia")

with col2:
    nivel = st.selectbox("Nível de Ensino", [
        "Fundamental 1", "Fundamental 2", "Ensino Médio", "Ensino Técnico/Superior"
    ])

# NOVO CAMPO: Contexto
contexto = st.text_area(
    "Contexto/Objetivo da Avaliação", 
    placeholder="Ex: Avaliar a capacidade de interpretação de texto e conhecimentos gerais sobre biomas. A prova deve ser desafiadora mas com linguagem acessível."
)

st.divider()

# 2. Estrutura da Prova
c1, c2, c3 = st.columns(3)
with c1:
    qtd_multipla = st.number_input("Qtd. Múltipla Escolha", min_value=0, value=4)
with c2:
    qtd_dissertativa = st.number_input("Qtd. Abertas", min_value=0, value=2)
with c3:
    dificuldade = st.selectbox("Dificuldade", ["Fácil", "Médio", "Difícil"])

# 3. Inclusão
st.divider()
incluir_adaptacao = st.checkbox("Incluir versão adaptada (TEA/Neurodivergentes)?")

# --- BOTÃO GERAR ---
if st.button("Gerar Avaliação", type="primary"):
    if not tema or not disciplina:
        st.warning("Preencha Tema e Disciplina.")
    else:
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
            client = genai.Client(api_key=api_key)
            
            with st.spinner('Criando avaliação...'):
                
                # PROMPT REFINADO
                prompt = f"""
                Atue como professor especialista. Crie uma prova sobre {tema} ({disciplina}, {nivel}).
                Dificuldade: {dificuldade}.
                
                CONTEXTO/OBJETIVO DO PROFESSOR:
                "{contexto if contexto else 'Avaliação geral de aprendizado.'}"
                
                REGRAS DE FORMATAÇÃO (RIGOROSO):
                1. NÃO crie cabeçalho para preencher nome, data ou escola. Comece direto pelo Título da Prova.
                2. Nas questões de múltipla escolha, coloque CADA alternativa em uma nova linha. (Ex: A)... [enter] B)...).
                3. Use Markdown padrão.
                
                ESTRUTURA:
                1. Título da Avaliação
                2. {qtd_multipla} questões de Múltipla Escolha.
                3. {qtd_dissertativa} questões Dissertativas.
                4. Gabarito no final.
                """
                
                if incluir_adaptacao:
                    prompt += """
                    ADICIONE UMA NOVA PÁGINA COM A VERSÃO ADAPTADA (TEA):
                    - Questões simplificadas.
                    - Fonte e espaçamento visualmente limpos.
                    - Sem metáforas ou pegadinhas.
                    """

                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=prompt
                )
                
                # --- APLICA A CORREÇÃO DE TEXTO ---
                # Aqui a gente pega o texto da IA e passa pela função que conserta as alternativas
                texto_corrigido = format_alternatives_vertical(response.text)
                
                st.session_state.prova_texto = texto_corrigido
                st.session_state.prova_tema = tema
                
        except Exception as e:
            st.error(f"Erro: {e}")

# --- EXIBIÇÃO ---
if "prova_texto" in st.session_state:
    st.markdown("---")
    st.subheader("Prévia:")
    st.markdown(st.session_state.prova_texto)
    
    try:
        # Converte Markdown para HTML
        html_body = markdown(st.session_state.prova_texto, extensions=['tables'])
        
        # Gera o PDF
        pdf_file = create_assessment_pdf(html_body)
        
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📄 Baixar Prova Formatada (PDF)",
                data=f.read(),
                file_name=f"prova_{st.session_state.prova_tema}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")