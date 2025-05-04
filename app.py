import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# --- FUNÇÃO PARA CRIAR PASTA TEMPORÁRIA ---
def criar_pasta_temp():
    if not os.path.exists("temp"):
        os.makedirs("temp")

# --- UPLOAD DO LOGO (CABEÇALHO) ---
st.sidebar.markdown("### 🔳 Configurações do Cabeçalho")
logo_escola = st.sidebar.file_uploader(
    "Carregar logo da escola (opcional)",
    type=["png", "jpg", "jpeg"],
    key="logo_uploader"
)

# --- CAMPOS PRINCIPAIS ---
nome_professor = st.text_input("Nome do Professor")
disciplina = st.text_input("Disciplina")
serie = st.selectbox(
    "Série/Turma",
    [
        "1º ano - Ensino Fundamental", "2º ano - Ensino Fundamental", "3º ano - Ensino Fundamental",
        "4º ano - Ensino Fundamental", "5º ano - Ensino Fundamental", "6º ano - Ensino Fundamental",
        "7º ano - Ensino Fundamental", "8º ano - Ensino Fundamental", "9º ano - Ensino Fundamental",
        "1º ano - Ensino Médio", "2º ano - Ensino Médio", "3º ano - Ensino Médio"
    ]
)
bimestre = st.selectbox("Bimestre", ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"])
data_prova = st.date_input("Data da Prova", value=date.today())

# --- GERENCIAMENTO DE QUESTÕES ---
if "questoes" not in st.session_state:
    st.session_state.questoes = []

st.subheader("✍️ Adicionar Questões")

# Seleção do tipo de questão
tipo_questao = st.selectbox(
    "Tipo de questão:",
    ["Dissertativa", "Múltipla Escolha"],
    key="tipo_questao"
)

# Campos para a questão
nova_questao = st.text_area("Texto da questão", key="nova_questao")
imagem_questao = st.file_uploader(
    "Imagem para a questão (opcional)",
    type=["png", "jpg", "jpeg"],
    key="imagem_questao"
)

# Campos adicionais para múltipla escolha
if tipo_questao == "Múltipla Escolha":
    col1, col2 = st.columns(2)
    with col1:
        opcao_a = st.text_input("Opção A", key="opcao_a")
        opcao_b = st.text_input("Opção B", key="opcao_b")
    with col2:
        opcao_c = st.text_input("Opção C", key="opcao_c")
        opcao_d = st.text_input("Opção D", key="opcao_d")
    resposta_correta = st.selectbox(
        "Resposta correta:",
        ["A", "B", "C", "D"],
        key="resposta_correta"
    )
else:
    opcao_a = opcao_b = opcao_c = opcao_d = resposta_correta = None

# Botão para adicionar questão
if st.button("➕ Adicionar Questão"):
    if nova_questao.strip():
        # Formata a questão conforme o tipo
        if tipo_questao == "Múltipla Escolha":
            questao_formatada = f"{nova_questao}\nA) {opcao_a}\nB) {opcao_b}\nC) {opcao_c}\nD) {opcao_d}\nResposta correta: {resposta_correta}"
        else:
            questao_formatada = nova_questao
        
        # Gerencia a imagem se houver
        if imagem_questao:
            criar_pasta_temp()
            imagem_path = os.path.join("temp", imagem_questao.name)
            with open(imagem_path, "wb") as f:
                f.write(imagem_questao.getbuffer())
            questao_formatada += f"\n[Imagem: {imagem_questao.name}]"
        
        st.session_state.questoes.append(questao_formatada)
        st.success("Questão adicionada!")
    else:
        st.warning("Por favor, insira o texto da questão.")

# --- VISUALIZAÇÃO DAS QUESTÕES ADICIONADAS ---
st.subheader("📋 Questões da Prova")
if not st.session_state.questoes:
    st.info("Nenhuma questão adicionada ainda.")
else:
    for i, questao in enumerate(st.session_state.questoes, 1):
        st.markdown(f"**Questão {i}**")
        st.text(questao)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✏️ Editar {i}", key=f"editar_{i}"):
                # Lógica para edição (implementar conforme necessário)
                pass
        with col2:
            if st.button(f"❌ Remover {i}", key=f"remover_{i}"):
                st.session_state.questoes.pop(i-1)
                st.experimental_rerun()

# --- GERAR DOCUMENTO WORD ---
st.subheader("📤 Gerar Prova")
if st.button("📄 Gerar Documento Word"):
    if not st.session_state.questoes:
        st.error("Adicione pelo menos uma questão!")
    else:
        doc = Document()
        
        # Configuração do estilo
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)
        
        # Adiciona logo se existir
        if logo_escola:
            criar_pasta_temp()
            logo_path = os.path.join("temp", logo_escola.name)
            with open(logo_path, "wb") as f:
                f.write(logo_escola.getbuffer())
            doc.add_picture(logo_path, width=Inches(1.5))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()
        
        # Cabeçalho da prova
        cabecalho = doc.add_paragraph()
        cabecalho.add_run(f"PROVA DE {disciplina.upper()}").bold = True
        cabecalho.add_run(f" - {bimestre.upper()}\n\n").bold = True
        cabecalho.add_run(f"Professor: {nome_professor}\n")
        cabecalho.add_run(f"Turma: {serie}\n")
        cabecalho.add_run(f"Data: {data_prova.strftime('%d/%m/%Y')}\n\n")
        cabecalho.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Adiciona questões
        for i, questao in enumerate(st.session_state.questoes, 1):
            # Verifica se há imagem na questão
            if "[Imagem:" in questao:
                texto, imagem_nome = questao.split("[Imagem:")
                texto = texto.strip()
                imagem_nome = imagem_nome.replace("]", "").strip()
                imagem_path = os.path.join("temp", imagem_nome)
                
                doc.add_paragraph(f"{i}. {texto}")
                try:
                    doc.add_picture(imagem_path, width=Inches(4.0))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                except:
                    st.error(f"Erro ao carregar imagem da questão {i}")
            else:
                doc.add_paragraph(f"{i}. {questao}")
            
            doc.add_paragraph()  # Espaço entre questões
        
        # Salva o documento
        nome_arquivo = f"Prova_{disciplina}_{serie}_{bimestre}.docx"
        doc.save(nome_arquivo)
        
        # Disponibiliza para download
        with open(nome_arquivo, "rb") as f:
            st.download_button(
                "⬇️ Baixar Prova",
                f,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        st.success("Documento gerado com sucesso!")
