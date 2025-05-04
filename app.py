import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
from io import BytesIO

# Configuração inicial
st.set_page_config("Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# Estados iniciais
if "questoes" not in st.session_state:
    st.session_state.questoes = []
if "editando" not in st.session_state:
    st.session_state.editando = None

# Sidebar - Configurações da prova
st.sidebar.header("⚙️ Cabeçalho da Prova")
logo_escola = st.sidebar.file_uploader("Logo da Escola", type=["png", "jpg", "jpeg"])
nome_professor = st.sidebar.text_input("Nome do Professor")
disciplina = st.sidebar.text_input("Disciplina")
serie = st.sidebar.selectbox("Série/Turma", [
    "1º ano - Fundamental", "2º ano - Fundamental", "3º ano - Fundamental",
    "4º ano - Fundamental", "5º ano - Fundamental", "6º ano - Fundamental",
    "7º ano - Fundamental", "8º ano - Fundamental", "9º ano - Fundamental",
    "1º ano - Médio", "2º ano - Médio", "3º ano - Médio"
])
bimestre = st.sidebar.selectbox("Bimestre", ["1º", "2º", "3º", "4º"])
data_prova = st.sidebar.date_input("Data da Prova", value=date.today())

# Formulário de questão
st.subheader("➕ Adicionar Questão" if st.session_state.editando is None else "✏️ Editar Questão")

with st.form("form_questao", clear_on_submit=False):
    tipo = st.radio("Tipo de Questão", ["Dissertativa", "Múltipla Escolha"], horizontal=True)
    texto = st.text_area("Enunciado", height=200)
    imagem = st.file_uploader("Imagem (opcional)", type=["png", "jpg", "jpeg"])

    opcoes = {}
    if tipo == "Múltipla Escolha":
        opcoes["A"] = st.text_input("Opção A")
        opcoes["B"] = st.text_input("Opção B")
        opcoes["C"] = st.text_input("Opção C")
        opcoes["D"] = st.text_input("Opção D")

    submitted = st.form_submit_button("Salvar Questão")
    if submitted:
        if texto.strip() == "":
            st.warning("⚠️ O enunciado é obrigatório.")
        else:
            questao = {
                "tipo": tipo,
                "texto": texto.strip(),
                "imagem": imagem.getvalue() if imagem else None,
                "nome_imagem": imagem.name if imagem else None,
                "opcoes": opcoes if tipo == "Múltipla Escolha" else None
            }

            if st.session_state.editando is not None:
                st.session_state.questoes[st.session_state.editando] = questao
                st.success("Questão editada com sucesso!")
                st.session_state.editando = None
            else:
                st.session_state.questoes.append(questao)
                st.success("Questão adicionada!")

            st.experimental_rerun()

# Lista de questões
st.subheader("📋 Questões")
for i, q in enumerate(st.session_state.questoes):
    st.markdown(f"**{i+1}. {q['texto']}**")
    if q["imagem"]:
        st.image(BytesIO(q["imagem"]), width=300)

    if q["tipo"] == "Múltipla Escolha":
        for letra, opcao in q["opcoes"].items():
            st.write(f"{letra}) {opcao}")
    else:
        st.markdown("_" * 50)

    col1, col2 = st.columns([1, 1])
    if col1.button("✏️ Editar", key=f"edit_{i}"):
        st.session_state.editando = i
        st.experimental_rerun()
    if col2.button("🗑️ Excluir", key=f"del_{i}"):
        st.session_state.questoes.pop(i)
        st.success("Questão excluída.")
        st.experimental_rerun()

# Exportar documento
st.subheader("📤 Gerar Documento Word")
if st.button("💾 Gerar Prova em Word"):
    if not st.session_state.questoes:
        st.error("Adicione ao menos uma questão.")
    else:
        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)

        # Cabeçalho
        if logo_escola:
            doc.add_picture(logo_escola, width=Inches(1.5))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph().add_run(f"PROVA DE {disciplina.upper()} - {bimestre}º BIMESTRE").bold = True
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Professor: {nome_professor}")
        doc.add_paragraph(f"Turma: {serie}")
        doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
        doc.add_paragraph("")

        # Questões
        for idx, q in enumerate(st.session_state.questoes, 1):
            doc.add_paragraph(f"{idx}. {q['texto']}")
            if q["imagem"]:
                try:
                    doc.add_picture(BytesIO(q["imagem"]), width=Inches(4))
                except:
                    doc.add_paragraph("[Erro ao carregar imagem]")

            if q["tipo"] == "Múltipla Escolha":
                for letra, texto in q["opcoes"].items():
                    doc.add_paragraph(f"{letra}) {texto}")
            else:
                for _ in range(4):
                    doc.add_paragraph("_" * 80)
            doc.add_paragraph()

        buffer = BytesIO()
        nome_doc = f"Prova_{disciplina}_{serie}_{bimestre}.docx".replace(" ", "_")
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "⬇️ Baixar Prova",
            data=buffer,
            file_name=nome_doc,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
