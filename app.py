import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# --- FUNÇÕES ---
def criar_pasta_temp():
    if not os.path.exists("temp"):
        os.makedirs("temp")

def limpar_pasta_temp():
    if os.path.exists("temp"):
        for file in os.listdir("temp"):
            os.remove(os.path.join("temp", file))

# --- UPLOAD DO LOGO ---
st.sidebar.header("Configurações do Cabeçalho")
logo_escola = st.sidebar.file_uploader(
    "📌 Upload do Logo (PNG/JPG)", 
    type=["png", "jpg", "jpeg"],
    key="logo_header"
)

# --- FORMULÁRIO PRINCIPAL ---
with st.form("dados_prova"):
    nome_professor = st.text_input("Nome do Professor")
    disciplina = st.text_input("Disciplina")
    serie = st.selectbox("Série/Turma", [
        "1º ano - Ensino Fundamental", "2º ano - Ensino Fundamental", 
        "3º ano - Ensino Fundamental", "4º ano - Ensino Fundamental",
        "5º ano - Ensino Fundamental", "6º ano - Ensino Fundamental",
        "7º ano - Ensino Fundamental", "8º ano - Ensino Fundamental",
        "9º ano - Ensino Fundamental", "1º ano - Ensino Médio",
        "2º ano - Ensino Médio", "3º ano - Ensino Médio"
    ])
    bimestre = st.selectbox("Bimestre", ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"])
    data_prova = st.date_input("Data da Prova", value=date.today())
    st.form_submit_button("Salvar Configurações")

# --- GERENCIAMENTO DE QUESTÕES ---
if "questoes" not in st.session_state:
    st.session_state.questoes = []

# --- ADIÇÃO DE QUESTÕES ---
st.subheader("✍️ Adicionar Questão")
tipo_questao = st.radio("Tipo:", ["Dissertativa", "Múltipla Escolha"], horizontal=True)
texto_questao = st.text_area("Texto da Questão", height=500)
imagem_questao = st.file_uploader("Imagem (opcional)", type=["png", "jpg", "jpeg"])

if tipo_questao == "Múltipla Escolha":
    col1, col2 = st.columns(2)
    with col1:
        opcao_a = st.text_input("Opção A")
        opcao_b = st.text_input("Opção B")
    with col2:
        opcao_c = st.text_input("Opção C")
        opcao_d = st.text_input("Opção D")

if st.button("➕ Adicionar Questão"):
    if texto_questao.strip():
        questao = {
            "texto": texto_questao,
            "tipo": tipo_questao,
            "imagem": None,
            "opcoes": None if tipo_questao == "Dissertativa" else {
                "A": opcao_a, "B": opcao_b, "C": opcao_c, "D": opcao_d
            }
        }
        
        if imagem_questao:
            criar_pasta_temp()
            img_path = os.path.join("temp", imagem_questao.name)
            with open(img_path, "wb") as f:
                f.write(imagem_questao.getbuffer())
            questao["imagem"] = img_path
        
        st.session_state.questoes.append(questao)
        st.success("Questão adicionada!")
    else:
        st.warning("Digite o texto da questão!")

# --- VISUALIZAÇÃO DAS QUESTÕES ---
st.subheader("📋 Pré-visualização da Prova")
if not st.session_state.questoes:
    st.info("Nenhuma questão adicionada")
else:
    for i, q in enumerate(st.session_state.questoes, 1):
        st.markdown(f"**Questão {i}:** {q['texto']}")
        if q["imagem"]:
            try:
                st.image(q["imagem"], width=400)
            except:
                st.warning("Não foi possível exibir a imagem.")
        if q["tipo"] == "Múltipla Escolha":
            st.write(f"A) {q['opcoes']['A']} | B) {q['opcoes']['B']}")
            st.write(f"C) {q['opcoes']['C']} | D) {q['opcoes']['D']}")
        st.write("---")

# --- GERAR DOCUMENTO WORD ---
st.subheader("📤 Exportar Prova")
if st.button("💾 Gerar Documento Word"):
    if not st.session_state.questoes:
        st.error("Adicione questões primeiro!")
    else:
        try:
            doc = Document()
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)

            if logo_escola:
                criar_pasta_temp()
                logo_path = os.path.join("temp", "logo_cabecalho." + logo_escola.name.split(".")[-1])
                with open(logo_path, "wb") as f:
                    f.write(logo_escola.getbuffer())
                doc.add_picture(logo_path, width=Inches(1.18))
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph()
            
            titulo = doc.add_paragraph()
            titulo.add_run(f"PROVA DE {disciplina.upper()}").bold = True
            titulo.add_run(f" - {bimestre.upper()}\n").bold = True
            titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_paragraph(f"Professor: {nome_professor}")
            doc.add_paragraph(f"Turma: {serie}")
            doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
            doc.add_paragraph("\n")

            for i, q in enumerate(st.session_state.questoes, 1):
                doc.add_paragraph(f"{i}. {q['texto']}")
                if q["imagem"]:
                    try:
                        doc.add_picture(q["imagem"], width=Inches(4.5))
                        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    except:
                        doc.add_paragraph("[Imagem não carregada]")

                if q["tipo"] == "Múltipla Escolha":
                    doc.add_paragraph(f"A) {q['opcoes']['A']}")
                    doc.add_paragraph(f"B) {q['opcoes']['B']}")
                    doc.add_paragraph(f"C) {q['opcoes']['C']}")
                    doc.add_paragraph(f"D) {q['opcoes']['D']}")
                else:
                    for _ in range(5):  # 5 linhas para resposta
                        doc.add_paragraph("_" * 100)

                doc.add_paragraph()

            nome_arquivo = f"Prova_{disciplina}_{serie}_{bimestre}.docx".replace(" ", "_")
            doc.save(nome_arquivo)

            with open(nome_arquivo, "rb") as f:
                st.download_button(
                    "⬇️ Baixar Prova",
                    data=f,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            limpar_pasta_temp()
            st.success("Documento gerado com sucesso!")

        except Exception as e:
            st.error(f"Erro: {str(e)}")
