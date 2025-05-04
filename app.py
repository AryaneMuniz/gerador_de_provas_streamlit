import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn
from datetime import date
import os

# Função para garantir que a pasta 'temp' exista
def criar_pasta_temp():
    if not os.path.exists("temp"):
        os.makedirs("temp")

# Configuração do título da página
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# Upload do logo (opcional)
logo_escola = st.file_uploader(
    "🔳 Carregar logo da escola (opcional)", 
    type=["png", "jpg", "jpeg"],
    help="Faça upload do logo para aparecer no cabeçalho da prova."
)

# Campos principais
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

# Lista de questões
if "questoes" not in st.session_state:
    st.session_state.questoes = []

st.subheader("✍️ Questões")

# Seleção de tipo de questão
tipo_questao = st.selectbox(
    "Selecione o tipo de questão:",
    ["Dissertativa", "Múltipla Escolha"]
)

# Adicionar nova questão
nova_questao = st.text_area("Digite a nova questão")
imagem_questao = st.file_uploader("Escolha uma imagem para a questão (opcional)", type=["jpg", "jpeg", "png"])

if tipo_questao == "Múltipla Escolha":
    opcao_a = st.text_input("Opção A")
    opcao_b = st.text_input("Opção B")
    opcao_c = st.text_input("Opção C")
    opcao_d = st.text_input("Opção D")
    resposta_correta = st.selectbox("Selecione a resposta correta:", ["A", "B", "C", "D"])
else:
    opcao_a = opcao_b = opcao_c = opcao_d = resposta_correta = None

if st.button("➕ Adicionar questão"):
    if nova_questao.strip() != "":
        if tipo_questao == "Múltipla Escolha" and (opcao_a and opcao_b and opcao_c and opcao_d):
            questao = f"{nova_questao}\nA) {opcao_a}\nB) {opcao_b}\nC) {opcao_c}\nD) {opcao_d}\nResposta correta: {resposta_correta}"
        else:
            questao = nova_questao
        
        if imagem_questao:
            criar_pasta_temp()
            imagem_path = os.path.join("temp", imagem_questao.name)
            with open(imagem_path, "wb") as f:
                f.write(imagem_questao.getbuffer())
            questao += f"\n[Imagem adicionada: {imagem_questao.name}]"
        
        st.session_state.questoes.append(questao.strip())
        st.success("Questão adicionada com sucesso!")
    else:
        st.warning("Digite algo antes de adicionar.")

# Mostrar questões já adicionadas
for i, q in enumerate(st.session_state.questoes):
    st.markdown(f"**{i+1}. {q}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✏️ Editar {i+1}", key=f"edit_{i}"):
            nova = st.text_area("Edite a questão:", value=q, key=f"edit_input_{i}")
            if st.button(f"💾 Salvar {i+1}", key=f"save_{i}"):
                st.session_state.questoes[i] = nova
                st.experimental_rerun()
    with col2:
        if st.button(f"❌ Remover {i+1}", key=f"remove_{i}"):
            st.session_state.questoes.pop(i)
            st.experimental_rerun()

# Gerar documento Word
st.subheader("📁 Gerar Arquivo Word")

if st.button("📥 Gerar prova em Word"):
    if not st.session_state.questoes:
        st.warning("⚠️ Adicione ao menos uma questão antes de gerar a prova.")
    else:
        doc = Document()

        # ===== CONFIGURAÇÃO DO DOCUMENTO =====
        # Define a fonte padrão para Arial 12
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(12)

        # Configura margens (2,5 cm em todos os lados)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1.0)  # 2,54 cm = 1 polegada
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # ===== CABEÇALHO COM LOGO =====
        # Se um logo foi carregado, adiciona ao documento
        if logo_escola:
            criar_pasta_temp()
            logo_path = os.path.join("temp", logo_escola.name)
            with open(logo_path, "wb") as f:
                f.write(logo_escola.getbuffer())
            
            # Adiciona o logo (ajustado para largura máxima de 3 polegadas)
            doc.add_picture(logo_path, width=Inches(1.5))  # Ajuste o tamanho conforme necessário
            last_paragraph = doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()  # Espaço após o logo

        # Título centralizado em negrito e tamanho 14
        titulo = doc.add_heading(f"PROVA DE {disciplina.upper()} – {bimestre.upper()}", level=0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        titulo_format = titulo.runs[0]
        titulo_format.bold = True
        titulo_format.font.size = Pt(14)

        # Adiciona informações da prova
        info_prova = [
            f"Professor: {nome_professor}",
            f"Disciplina: {disciplina}",
            f"Série/Turma: {serie}",
            f"Bimestre: {bimestre}",
            f"Data: {data_prova.strftime('%d/%m/%Y')}"
        ]

        for info in info_prova:
            p = doc.add_paragraph(info)
            p.paragraph_format.space_after = Pt(6)  # Espaçamento entre linhas

        doc.add_paragraph(" ")  # Espaço extra antes das questões

        # ===== QUESTÕES =====
        for i, questao in enumerate(st.session_state.questoes, 1):
            if "[Imagem adicionada:" in questao:
                # Separa o texto da imagem
                texto_questao, imagem_nome = questao.split("[Imagem adicionada:")
                texto_questao = texto_questao.strip()
                imagem_nome = imagem_nome.replace("]", "").strip()
                imagem_path = os.path.join("temp", imagem_nome)
                
                # Adiciona o texto da questão
                p = doc.add_paragraph(f"{i}. {texto_questao}")
                p.paragraph_format.space_after = Pt(12)  # Espaçamento maior após questão
                
                # Adiciona a imagem centralizada
                try:
                    doc.add_picture(imagem_path, width=Inches(4.0))
                    last_paragraph = doc.paragraphs[-1]
                    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                except Exception as e:
                    st.error(f"Erro ao adicionar a imagem: {e}")
            else:
                p = doc.add_paragraph(f"{i}. {questao}")
                p.paragraph_format.space_after = Pt(12)  # Espaçamento entre questões

        # Salva o arquivo
        nome_arquivo = f"prova_{disciplina.upper()}_{serie} ({bimestre}).docx"
        doc.save(nome_arquivo)

        # Botão para download
        with open(nome_arquivo, "rb") as file:
            st.download_button(
                label="📥 Baixar Prova",
                data=file,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
