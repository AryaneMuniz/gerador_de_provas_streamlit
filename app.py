import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
from io import BytesIO

st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# Inicializa estado
if "questoes" not in st.session_state:
    st.session_state.questoes = []

# --- Cabeçalho ---
st.sidebar.header("Cabeçalho da Prova")
logo_escola = st.sidebar.file_uploader("📌 Logo da Escola (PNG/JPG)", type=["png", "jpg", "jpeg"])

# --- Informações da Prova ---
with st.form("form_info"):
    st.subheader("📄 Informações da Prova")
    professor = st.text_input("Nome do Professor")
    disciplina = st.text_input("Disciplina")
    serie = st.selectbox("Série/Turma", [
        "1º ano - EF", "2º ano - EF", "3º ano - EF", "4º ano - EF", "5º ano - EF",
        "6º ano - EF", "7º ano - EF", "8º ano - EF", "9º ano - EF",
        "1º ano - EM", "2º ano - EM", "3º ano - EM"
    ])
    bimestre = st.selectbox("Bimestre", ["1º", "2º", "3º", "4º"])
    data_prova = st.date_input("Data da Prova", value=date.today())
    st.form_submit_button("Salvar")

# --- Formulário de Questão ---
st.subheader("➕ Adicionar Questão")

with st.form("form_questao"):
    tipo = st.radio("Tipo de Questão", ["Dissertativa", "Múltipla Escolha"], horizontal=True)
    texto = st.text_area("Texto da Questão", height=150)
    imagem = st.file_uploader("Imagem (opcional)", type=["png", "jpg", "jpeg"], key="imagem_questao")

    opcoes = {"A": "", "B": "", "C": "", "D": ""}
    if tipo == "Múltipla Escolha":
        opcoes["A"] = st.text_input("Opção A", key="opt_a")
        opcoes["B"] = st.text_input("Opção B", key="opt_b")
        opcoes["C"] = st.text_input("Opção C", key="opt_c")
        opcoes["D"] = st.text_input("Opção D", key="opt_d")

    submitted = st.form_submit_button("Adicionar")

    if submitted:
        if not texto.strip():
            st.warning("Por favor, escreva o texto da questão.")
        else:
            nova_questao = {
                "texto": texto,
                "tipo": tipo,
                "imagem": imagem.getvalue() if imagem else None,
                "opcoes": opcoes if tipo == "Múltipla Escolha" else None
            }
            st.session_state.questoes.append(nova_questao)
            st.success("Questão adicionada com sucesso!")

# --- Visualizar Questões ---
st.subheader("📋 Questões Adicionadas")
for i, q in enumerate(st.session_state.questoes, 1):
    st.markdown(f"**{i}. {q['texto']}**")
    if q["imagem"]:
        st.image(BytesIO(q["imagem"]), width=350)

    if q["tipo"] == "Múltipla Escolha" and q["opcoes"]:
        for letra, texto in q["opcoes"].items():
            st.markdown(f"- {letra}) {texto}")
    else:
        st.markdown("_" * 50)

# --- Exportar Prova ---
st.subheader("📤 Exportar Prova")
if st.button("💾 Gerar Documento Word"):
    if not st.session_state.questoes:
        st.error("Adicione pelo menos uma questão.")
    else:
        try:
            doc = Document()
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)

            # Logo
            if logo_escola:
                doc.add_picture(logo_escola, width=Inches(1.2))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph()

            # Título
            titulo = doc.add_paragraph()
            titulo.add_run(f"PROVA DE {disciplina.upper()} - {bimestre}º BIMESTRE\n").bold = True
            titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_paragraph(f"Professor: {professor}")
            doc.add_paragraph(f"Turma: {serie}")
            doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
            doc.add_paragraph("\n")

            # Questões
            for i, q in enumerate(st.session_state.questoes, 1):
                doc.add_paragraph(f"{i}. {q['texto']}")
                if q["imagem"]:
                    try:
                        doc.add_picture(BytesIO(q["imagem"]), width=Inches(4.5))
                        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    except:
                        doc.add_paragraph("[Erro ao carregar imagem]")

                if q["tipo"] == "Múltipla Escolha" and q["opcoes"]:
                    for letra, texto in q["opcoes"].items():
                        doc.add_paragraph(f"{letra}) {texto}")
                else:
                    for _ in range(5):
                        doc.add_paragraph("_" * 80)
                doc.add_paragraph()

            # Exportar
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            nome_arquivo = f"Prova_{disciplina}_{serie}_{bimestre}Bim.docx".replace(" ", "_")

            st.download_button(
                label="⬇️ Baixar Prova",
                data=buffer,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Erro ao gerar documento: {e}")
