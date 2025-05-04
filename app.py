import streamlit as st
from docx import Document
from docx.shared import Inches
from datetime import date
import os

# Função para garantir que a pasta 'temp' exista
def criar_pasta_temp():
    if not os.path.exists("temp"):
        os.makedirs("temp")

# Configuração do título da página
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

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
            # Formatação para questões de múltipla escolha
            questao = f"{nova_questao}\nA) {opcao_a}\nB) {opcao_b}\nC) {opcao_c}\nD) {opcao_d}\nResposta correta: {resposta_correta}"
        else:
            # Questão dissertativa
            questao = nova_questao
        
        # Se uma imagem foi carregada, salvar e adicionar ao arquivo temporário
        if imagem_questao:
            # Chamar a função para garantir que a pasta 'temp' exista
            criar_pasta_temp()
            
            # Defina um caminho temporário para a imagem
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

        # TÍTULO PERSONALIZADO (com disciplina e bimestre)
        doc.add_heading(f"PROVA DE {disciplina.upper()} – {bimestre.upper()}", 0)

        # Informações adicionais
        doc.add_paragraph(f"Professor: {nome_professor}")
        doc.add_paragraph(f"Disciplina: {disciplina}")
        doc.add_paragraph(f"Série/Turma: {serie}")
        doc.add_paragraph(f"Bimestre: {bimestre}")
        doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
        doc.add_paragraph(" ")

        # Adicionar questões no documento
        for i, questao in enumerate(st.session_state.questoes, 1):
            # Verifica se a questão contém a marca de imagem
            if "[Imagem adicionada:" in questao:
                # Extrai o nome da imagem
                imagem_nome = questao.split(": ")[-1].replace("]", "")
                imagem_path = os.path.join("temp", imagem_nome)
                
                # Adiciona o texto da questão
                doc.add_paragraph(f"{i}. {questao.split('[Imagem adicionada:')[0].strip()}")
                
                # Tenta adicionar a imagem ao Word
                try:
                    doc.add_picture(imagem_path, width=Inches(4.0))  # Ajusta a imagem no documento
                except Exception as e:
                    st.error(f"Erro ao adicionar a imagem: {e}")
            else:
                doc.add_paragraph(f"{i}. {questao}")

        # Salvar o arquivo
        doc_path = "prova_gerada.docx"
        doc.save(doc_path)

        # Botão para download
        with open(doc_path, "rb") as file:
            st.download_button(
                label="📥 Baixar Prova",
                data=file,
                file_name=doc_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
