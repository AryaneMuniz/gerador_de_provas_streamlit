import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
from io import BytesIO

st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# --- Inicialização do estado ---
if "questoes" not in st.session_state:
    st.session_state.questoes = []
if "editando_index" not in st.session_state:
    st.session_state.editando_index = None

# --- Cabeçalho da escola ---
st.sidebar.header("Configurações do Cabeçalho")
logo_escola = st.sidebar.file_uploader(
    "📌 Upload do Logo (PNG/JPG)", 
    type=["png", "jpg", "jpeg"],
    key="logo_header"
)

# --- Formulário de dados principais ---
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

# --- Formulário de questões ---
modo = "✏️ Editar Questão" if st.session_state.editando_index is not None else "➕ Adicionar Questão"
st.subheader(modo)

# Limpeza dos campos após adicionar a questão
if "texto_questao" not in st.session_state:
    st.session_state.texto_questao = ""
if "imagem_questao" not in st.session_state:
    st.session_state.imagem_questao = None
if "opcao_a" not in st.session_state:
    st.session_state.opcao_a = ""
if "opcao_b" not in st.session_state:
    st.session_state.opcao_b = ""
if "opcao_c" not in st.session_state:
    st.session_state.opcao_c = ""
if "opcao_d" not in st.session_state:
    st.session_state.opcao_d = ""

# Tipo de questão
tipo_questao = st.radio("Tipo:", ["Dissertativa", "Múltipla Escolha"], horizontal=True)

# Campos da questão
texto_questao = st.text_area("Texto da Questão", height=250, value=st.session_state.texto_questao)
imagem_questao = st.file_uploader("Imagem (opcional)", type=["png", "jpg", "jpeg"], key="img_quest", label_visibility="collapsed")

# Mostrar opções apenas se for "Múltipla Escolha"
if tipo_questao == "Múltipla Escolha":
    opcao_a = st.text_input("Opção A", value=st.session_state.opcao_a)
    opcao_b = st.text_input("Opção B", value=st.session_state.opcao_b)
    opcao_c = st.text_input("Opção C", value=st.session_state.opcao_c)
    opcao_d = st.text_input("Opção D", value=st.session_state.opcao_d)
else:
    # Limpar as opções caso a questão seja dissertativa
    st.session_state.opcao_a = ""
    st.session_state.opcao_b = ""
    st.session_state.opcao_c = ""
    st.session_state.opcao_d = ""

# Ao clicar no botão de adicionar/editar
if st.button(modo):
    if texto_questao.strip():
        nova_questao = {
            "texto": texto_questao,
            "tipo": tipo_questao,
            "imagem": imagem_questao.getvalue() if imagem_questao else None,
            "nome_imagem": imagem_questao.name if imagem_questao else None,
            "opcoes": None if tipo_questao == "Dissertativa" else {
                "A": opcao_a, "B": opcao_b, "C": opcao_c, "D": opcao_d
            }
        }

        if st.session_state.editando_index is not None:
            st.session_state.questoes[st.session_state.editando_index] = nova_questao
            st.session_state.editando_index = None
            st.success("Questão editada com sucesso!")
        else:
            st.session_state.questoes.append(nova_questao)
            st.session_state.texto_questao = ""  # Limpar campo do texto da questão
            st.session_state.imagem_questao = None  # Limpar o campo da imagem
            st.session_state.opcao_a = ""  # Limpar a opção A
            st.session_state.opcao_b = ""  # Limpar a opção B
            st.session_state.opcao_c = ""  # Limpar a opção C
            st.session_state.opcao_d = ""  # Limpar a opção D
            st.success("Questão adicionada!")

    else:
        st.warning("Digite o texto da questão!")

# --- Visualização com opções de editar e excluir ---
st.subheader("📋 Questões Adicionadas")

for i, q in enumerate(st.session_state.questoes):
    st.markdown(f"**Questão {i+1}:** {q['texto']}")
    if q["imagem"]:
        st.image(BytesIO(q["imagem"]), width=350)

    if q["tipo"] == "Múltipla Escolha":
        st.write(f"A) {q['opcoes']['A']}")
        st.write(f"B) {q['opcoes']['B']}")
        st.write(f"C) {q['opcoes']['C']}")
        st.write(f"D) {q['opcoes']['D']}")
    else:
        st.markdown("_" * 60)

    col_editar, col_excluir = st.columns([1, 1])
    if col_editar.button("✏️ Editar", key=f"editar_{i}"):
        st.session_state.editando_index = i
        st.experimental_rerun()
    if col_excluir.button("🗑️ Excluir", key=f"excluir_{i}"):
        st.session_state.questoes.pop(i)
        st.experimental_rerun()

# --- Exportação da Prova ---
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
                doc.add_picture(logo_escola, width=Inches(1.2))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph()

            titulo = doc.add_paragraph()
            titulo.add_run(f"PROVA DE {disciplina.upper()} - {bimestre.upper()}\n").bold = True
            titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_paragraph(f"Professor: {nome_professor}")
            doc.add_paragraph(f"Turma: {serie}")
            doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
            doc.add_paragraph("\n")

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
            doc.save(buffer)  # Salvar corretamente
            buffer.seek(0)

            st.download_button(
                "⬇️ Baixar Prova",
                data=buffer,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml
