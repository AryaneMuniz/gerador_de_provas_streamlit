import streamlit as st
from docx import Document
from datetime import date

# Título do app
st.title("📄 Gerador de Provas para Professores")

# Inputs básicos
nome_professor = st.text_input("Nome do professor")
disciplina = st.text_input("Disciplina")
serie = st.text_input("Série/Turma")
data_prova = st.date_input("Data da prova", value=date.today())

# Área para adicionar questões
st.subheader("➕ Adicionar questões")

questoes = []

for i in range(1, 6):  # 5 perguntas
    st.markdown(f"**Questão {i}**")
    tipo = st.selectbox(f"Tipo da questão {i}", ["Discursiva", "Múltipla escolha"], key=f"tipo_{i}")
    enunciado = st.text_area(f"Enunciado da questão {i}", key=f"enunciado_{i}")
    
    alternativas = []
    if tipo == "Múltipla escolha":
        alternativas.append(st.text_input(f"A)", key=f"a_{i}"))
        alternativas.append(st.text_input(f"B)", key=f"b_{i}"))
        alternativas.append(st.text_input(f"C)", key=f"c_{i}"))
        alternativas.append(st.text_input(f"D)", key=f"d_{i}"))
    
    questoes.append({
        "tipo": tipo,
        "enunciado": enunciado,
        "alternativas": alternativas
    })

# Botão para gerar prova
if st.button("📁 Gerar prova em Word"):
    doc = Document()

    # Cabeçalho da prova
    doc.add_heading('Prova', 0)
    doc.add_paragraph(f"Professor: {nome_professor}")
    doc.add_paragraph(f"Disciplina: {disciplina}")
    doc.add_paragraph(f"Série/Turma: {serie}")
    doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
    doc.add_paragraph(" ")

    # Questões
    for i, q in enumerate(questoes):
        doc.add_paragraph(f"{i+1}. {q['enunciado']}")
        if q["tipo"] == "Múltipla escolha":
            for letra, alt in zip("ABCD", q["alternativas"]):
                doc.add_paragraph(f"   {letra}) {alt}")
        else:
            doc.add_paragraph("   ___________________________________________")
            doc.add_paragraph("   ___________________________________________")
            doc.add_paragraph("   ___________________________________________")

        doc.add_paragraph(" ")

    # Salva o arquivo
    nome_arquivo = f"prova_{disciplina}_{serie}.docx"
    doc.save(nome_arquivo)
    with open(nome_arquivo, "rb") as file:
        st.download_button("📥 Baixar prova", file, file_name=nome_arquivo)

    st.success("✅ Prova gerada com sucesso!")
