import streamlit as st
from docx import Document
from datetime import date

st.title("📄 Gerador de Provas para Professores")

# Inicializa lista de questões na sessão
if "questoes" not in st.session_state:
    st.session_state.questoes = []

# Cabeçalho da prova
nome_professor = st.text_input("Nome do professor")
disciplina = st.text_input("Disciplina")
serie = st.selectbox(
    "Série/Turma",
    [
        "1º ano - Ensino Fundamental",
        "2º ano - Ensino Fundamental",
        "3º ano - Ensino Fundamental",
        "4º ano - Ensino Fundamental",
        "5º ano - Ensino Fundamental",
        "6º ano - Ensino Fundamental",
        "7º ano - Ensino Fundamental",
        "8º ano - Ensino Fundamental",
        "9º ano - Ensino Fundamental",
        "1º ano - Ensino Médio",
        "2º ano - Ensino Médio",
        "3º ano - Ensino Médio"
    ]
)
bimestre = st.selectbox("Bimestre", ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"])
data_prova = st.date_input("Data da prova", value=date.today())

st.divider()

st.header("➕ Adicionar nova questão")

tipo = st.selectbox("Tipo da questão", ["Discursiva", "Múltipla escolha"])
enunciado = st.text_area("Enunciado da questão")

alternativas = []
if tipo == "Múltipla escolha":
    alternativas.append(st.text_input("A)"))
    alternativas.append(st.text_input("B)"))
    alternativas.append(st.text_input("C)"))
    alternativas.append(st.text_input("D)"))

# Botão para adicionar questão
if st.button("Adicionar questão"):
    nova_questao = {
        "tipo": tipo,
        "enunciado": enunciado,
        "alternativas": alternativas if tipo == "Múltipla escolha" else []
    }
    st.session_state.questoes.append(nova_questao)
    st.success("✅ Questão adicionada!")

st.divider()
st.header("📋 Lista de questões")

# Exibir questões com botões para editar/remover
for idx, q in enumerate(st.session_state.questoes):
    with st.expander(f"Questão {idx+1}"):
        st.write(f"**Tipo:** {q['tipo']}")
        st.write(f"**Enunciado:** {q['enunciado']}")
        if q["tipo"] == "Múltipla escolha":
            for letra, alt in zip("ABCD", q["alternativas"]):
                st.write(f"{letra}) {alt}")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ Remover", key=f"remover_{idx}"):
                st.session_state.questoes.pop(idx)
                st.experimental_rerun()

# Botão para gerar prova
st.divider()
if st.button("📁 Gerar prova em Word"):
    if not st.session_state.questoes:
        st.warning("⚠️ Adicione ao menos uma questão antes de gerar a prova.")
    else:
        doc = Document()
       doc.add_heading(f"PROVA DE {disciplina.upper()} – {bimestre.upper()}", 0)
        doc.add_paragraph(f"Professor: {nome_professor}")
        doc.add_paragraph(f"Disciplina: {disciplina}")
        doc.add_paragraph(f"Série/Turma: {serie}")
        doc.add_paragraph(f"Bimestre: {bimestre}")
        doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
        doc.add_paragraph(" ")

        for i, q in enumerate(st.session_state.questoes):
            doc.add_paragraph(f"{i+1}. {q['enunciado']}")
            if q["tipo"] == "Múltipla escolha":
                for letra, alt in zip("ABCD", q["alternativas"]):
                    doc.add_paragraph(f"   {letra}) {alt}")
            else:
                doc.add_paragraph("   ______________________________")
                doc.add_paragraph("   ______________________________")
                doc.add_paragraph("   ______________________________")
            doc.add_paragraph(" ")

        nome_arquivo = f"prova_{disciplina}_{serie}.docx"
        doc.save(nome_arquivo)
        with open(nome_arquivo, "rb") as file:
            st.download_button("📥 Baixar prova", file, file_name=nome_arquivo)

        st.success("✅ Prova gerada com sucesso!")
