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
    nome_escola = st.text_input("Nome da Escola")
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

with st.form("form_questao", clear_on_submit=True):
    tipo = st.radio("Tipo de Questão", ["Dissertativa", "Múltipla Escolha"], horizontal=True, key="tipo_questao")
    texto = st.text_area("Texto da Questão", height=150, key="texto_questao")
    imagem = st.file_uploader("Imagem (opcional)", type=["png", "jpg", "jpeg"], key="imagem_questao")

    # Opções de múltipla escolha (só aparece se o tipo for Múltipla Escolha)
    if tipo == "Múltipla Escolha":
        st.write("Opções de resposta:")
        col1, col2 = st.columns(2)
        with col1:
            opcao_a = st.text_input("Opção A", value="", key="opt_a")
            opcao_c = st.text_input("Opção C", value="", key="opt_c")
        with col2:
            opcao_b = st.text_input("Opção B", value="", key="opt_b")
            opcao_d = st.text_input("Opção D", value="", key="opt_d")
        opcoes = {'A': opcao_a, 'B': opcao_b, 'C': opcao_c, 'D': opcao_d}
    else:
        opcoes = None

    submitted = st.form_submit_button("Adicionar Questão")

    if submitted:
        if not texto.strip():
            st.warning("Por favor, escreva o texto da questão.")
        elif tipo == "Múltipla Escolha" and any(v.strip() == "" for v in opcoes.values()):
            st.warning("Preencha todas as opções da múltipla escolha.")
        else:
            nova_questao = {
                "texto": texto,
                "tipo": tipo,
                "imagem": imagem.read() if imagem else None,
                "opcoes": opcoes if tipo == "Múltipla Escolha" else None
            }
            st.session_state.questoes.append(nova_questao)
            st.success("Questão adicionada com sucesso!")
            st.rerun()

# --- Lista de Questões ---
st.subheader("📋 Questões Adicionadas")

if not st.session_state.questoes:
    st.info("Nenhuma questão adicionada ainda.")
else:
    for i, q in enumerate(st.session_state.questoes, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {q['texto']}**")
            if q["imagem"]:
                st.image(BytesIO(q["imagem"]), width=350)
            if q["tipo"] == "Múltipla Escolha":
                st.write(f"A) {q['opcoes']['A']}")
                st.write(f"B) {q['opcoes']['B']}")
                st.write(f"C) {q['opcoes']['C']}")
                st.write(f"D) {q['opcoes']['D']}")
            else:
                st.markdown("_" * 60)

            if st.button(f"🗑️ Excluir Questão {i}", key=f"del_{i}"):
                st.session_state.questoes.pop(i-1)
                st.rerun()

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

        # Cabeçalho com logo
        if logo_escola:
            logo_escola.seek(0)
            doc.add_picture(logo_escola, width=Inches(1.5))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Informações da prova
        doc.add_paragraph(nome_escola, style='Heading 1').alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
        doc.add_paragraph(f"Disciplina: {disciplina}").bold = True
        doc.add_paragraph(f"Professor: {nome_professor}")
        doc.add_paragraph(f"Turma: {serie}")
        doc.add_paragraph(f"Bimestre: {bimestre}")
        doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
        doc.add_paragraph()
        doc.add_paragraph("Prova Escrita").bold = True
        doc.add_paragraph()

        # Adicionar questões
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
                for _ in range(5):  # Linhas para resposta dissertativa
                    doc.add_paragraph("_" * 80)
            doc.add_paragraph()

        # Salvar documento
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
