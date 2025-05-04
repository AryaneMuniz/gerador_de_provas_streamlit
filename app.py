import streamlit as st
from docx import Document

# Função para adicionar pergunta
def adicionar_pergunta(texto, tipo, alternativas):
    if tipo == "m":
        if not (alternativas["A"] and alternativas["B"] and alternativas["C"] and alternativas["D"]):
            return None  # Retorna None se não tiver alternativas completas
        return {"texto": texto, "tipo": tipo, "alternativas": alternativas}
    else:
        return {"texto": texto, "tipo": tipo}

# Função para gerar a prova
def gerar_prova(titulo, perguntas):
    doc = Document()
    doc.add_heading(titulo, 0)
    doc.add_paragraph("Nome do aluno: ____________________________\n")

    for i, p in enumerate(perguntas, 1):
        doc.add_paragraph(f"{i}. {p['texto']}")
        if p["tipo"] == "m":
            doc.add_paragraph(f"( ) A: {p['alternativas']['A']}    ( ) B: {p['alternativas']['B']}    ( ) C: {p['alternativas']['C']}    ( ) D: {p['alternativas']['D']}")
        else:
            doc.add_paragraph("Resposta: ______________________________")
            doc.add_paragraph("_______________________________________")
            doc.add_paragraph("_______________________________________")

    doc.save("prova_gerada.docx")
    return "Prova gerada com sucesso como 'prova_gerada.docx'!"

# Interface com Streamlit
st.title("Gerador de Provas")
st.write("Crie sua prova com perguntas dissertativas e múltipla escolha.")

# Entrada de título da prova
titulo = st.text_input("Título da Prova:")

# Lista para armazenar perguntas
perguntas = []

# Caixa de pergunta
texto_pergunta = st.text_area("Digite a pergunta:")

# Escolha de tipo de pergunta (dissertativa ou múltipla escolha)
tipo = st.radio("Tipo da Pergunta", ("Dissertativa", "Múltipla Escolha"))

# Inputs para alternativas (só visíveis se for múltipla escolha)
alternativas = {}
if tipo == "Múltipla Escolha":
    alternativas["A"] = st.text_input("Alternativa A")
    alternativas["B"] = st.text_input("Alternativa B")
    alternativas["C"] = st.text_input("Alternativa C")
    alternativas["D"] = st.text_input("Alternativa D")

# Botão para adicionar a pergunta
if st.button("Adicionar Pergunta"):
    if not texto_pergunta:
        st.warning("Digite a pergunta antes de adicionar.")
    elif tipo == "Múltipla Escolha" and not (alternativas["A"] and alternativas["B"] and alternativas["C"] and alternativas["D"]):
        st.warning("Preencha todas as alternativas A, B, C e D.")
    else:
        pergunta = adicionar_pergunta(texto_pergunta, tipo, alternativas)
        if pergunta:
            perguntas.append(pergunta)
            st.success("Pergunta adicionada com sucesso!")
        else:
            st.error("Erro ao adicionar pergunta.")

# Exibição das perguntas adicionadas
if perguntas:
    st.write("Perguntas Adicionadas:")
    for idx, pergunta in enumerate(perguntas, 1):
        st.write(f"{idx}. {pergunta['texto']}")
        if pergunta["tipo"] == "m":
            st.write(f"Alternativas: A: {pergunta['alternativas']['A']}, B: {pergunta['alternativas']['B']}, C: {pergunta['alternativas']['C']}, D: {pergunta['alternativas']['D']}")
        else:
            st.write("Tipo: Dissertativa")

# Botão para gerar a prova
if st.button("Gerar Prova"):
    if not titulo:
        st.warning("Digite o título da prova.")
    elif not perguntas:
        st.warning("Adicione pelo menos uma pergunta.")
    else:
        resultado = gerar_prova(titulo, perguntas)
        st.success(resultado)
        st.download_button("Baixar Prova", data=open("prova_gerada.docx", "rb").read(), file_name="prova_gerada.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
