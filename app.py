import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
from io import BytesIO

st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# Inicializa o estado da sessão
if "questoes" not in st.session_state:
    st.session_state.questoes = []

# --- Cabeçalho da escola ---
st.sidebar.header("Configurações do Cabeçalho")
logo_escola = st.sidebar.file_uploader("📌 Logo da Escola", type=["png", "jpg", "jpeg"])

# --- Dados da prova ---
with st.form("form_dados"):
    st.subheader("📘 Dados da Prova")
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
    st.form_submit_button("Salvar Dados")

# --- Adicionar Questão ---
st.subheader("➕ Adicionar Questão")

with st.form("form_questao"):
    tipo = st.radio("Tipo de Questão", ["Dissertativa", "Múltipla Escolha"], horizontal=True)
    texto = st.text_area("Texto da Questão", height=150)
    imagem = st.file_uploader("Imagem (opcional)", type=["png", "jpg", "jpeg"], key="imagem_questao")

    opcoes = {}
    if tipo == "Múltipla Escolha":
        col1, col2 = st.columns(2)
        with col1:
            opcoes["A"] = st.text_input("Opção A", key="opt_a")
            opcoes["C"] = st.text_input("Opção C", key="opt_c")
        with col2:
            opcoes["B"] = st.text_input("Opção B", key="opt_b")
            opcoes["D"] = st.text_input("Opção D", key="opt_d")

    submitted = st.form_submit_button("Adicionar")

    if submitted:
        if not texto.strip():
            st.warning("Por favor, escreva o texto da questão.")
        elif tipo == "Múltipla Escolha" and any(v.strip() == "" for v in opcoes.values()):
            st.warning("Preencha todas as opções da múltipla escolha.")
        else:
            nova_questao = {
                "texto": texto,
                "tipo": tipo,
                "imagem": imagem.getvalue() if imagem else None,
                "opcoes": opcoes if tipo == "Múltipla Escolha" else None
            }
            st.session_state.questoes.append(nova_questao)
            st.success("Questão adicionada com sucesso!")

# --- Lista de Questões ---
st.subheader("📋 Questões Adicionadas")

for i, q in enumerate(st.session_state.questoes):
    st.markdown(f"**{i+1}. {q['texto']}**")
    if q["imagem"]:
        st.image(BytesIO(q["imagem"]), width=350)
    if q["tipo"] == "Múltipla Escolha":
        st.write(f"A) {q['opcoes']['A']}")
        st.write(f"B) {q['opcoes']['B']}")
        st.write(f"C) {q['opcoes']['C']}")
        st.write(f"D) {q['opcoes']['D']}")
    else:
        st.markdown("_" * 60)

    if st.button(f"🗑️ Excluir Questão {i+1}", key=f"del_{i}"):
        st.session_state.questoes.pop(i)
        st.experimental_rerun()

# --- Exportar para Word ---
st.subheader("📤 Exportar Prova")

if st.button("💾 Gerar Documento Word"):
    if not st.session_state.questoes:
        st.error("Adicione ao menos uma questão antes de exportar.")
    else:
        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)

        if logo_escola:
            doc.add_picture(logo_escola, width=Inches(1.2))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()
        titulo = doc.add_paragraph()
        titulo.add_run(f"PROVA DE {disciplina.upper()} - {bimestre.upper()}").bold = True
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Professor: {nome_professor}")
        doc.add_paragraph(f"Turma: {serie}")
        doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
        doc.add_paragraph()

        for i, q in enumerate(st.session_state.questoes, 1):
            doc.add_paragraph(f"{i}. {q['texto']}")
            if q["imagem"]:
                try:
                    doc.add_picture(BytesIO(q["imagem"]), width=Inches(4.5))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                except:
                    doc.add_paragraph("[Erro ao carregar imagem]")
            if q["tipo"] == "Múltipla Escolha":
                doc.add_paragraph(f"A) {q['opcoes']['A']}")
                doc.add_paragraph(f"B) {q['opcoes']['B']}")
                doc.add_paragraph(f"C) {q['opcoes']['C']}")
                doc.add_paragraph(f"D) {q['opcoes']['D']}")
            else:
                for _ in range(5):
                    doc.add_paragraph("_" * 80)
            doc.add_paragraph()

        nome_arquivo = f"Prova_{disciplina}_{serie}_{bimestre}.docx".replace(" ", "_")
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar Prova",
            data=buffer,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
