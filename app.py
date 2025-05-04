import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
from io import BytesIO

# Configuração inicial
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# --- Inicialização do estado ---
if "questoes" not in st.session_state:
    st.session_state.questoes = []
if "editando_index" not in st.session_state:
    st.session_state.editando_index = None
if "texto_questao" not in st.session_state:
    st.session_state.texto_questao = ""
if "imagem_questao" not in st.session_state:
    st.session_state.imagem_questao = None
if "opcoes" not in st.session_state:
    st.session_state.opcoes = {"A": "", "B": "", "C": "", "D": ""}
if "tipo_questao" not in st.session_state:
    st.session_state.tipo_questao = "Dissertativa"

# --- Cabeçalho da escola ---
with st.sidebar:
    st.header("Configurações do Cabeçalho")
    logo_escola = st.file_uploader(
        "📌 Logo da Escola (PNG/JPG)", 
        type=["png", "jpg", "jpeg"]
    )

# --- Formulário de dados principais ---
with st.form("dados_prova"):
    st.subheader("📋 Dados da Prova")
    nome_escola = st.text_input("Nome da Escola")
    nome_professor = st.text_input("Nome do Professor*", placeholder="Obrigatório")
    disciplina = st.text_input("Disciplina*", placeholder="Obrigatório")
    serie = st.selectbox("Série/Turma*", [
        "1º ano - Ensino Fundamental", "2º ano - Ensino Fundamental", 
        # ... (opções mantidas iguais)
    ])
    bimestre = st.selectbox("Bimestre*", ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"])
    data_prova = st.date_input("Data da Prova*", value=date.today())
    st.form_submit_button("Salvar Configurações")

# --- Formulário de questões ---
st.subheader("✍️ Editor de Questões")
st.session_state.tipo_questao = st.radio(
    "Tipo de Questão*", 
    ["Dissertativa", "Múltipla Escolha"], 
    horizontal=True
)

# Campos comuns
texto_questao = st.text_area(
    "Texto da Questão*", 
    height=150, 
    value=st.session_state.texto_questao,
    placeholder="Digite o enunciado da questão..."
)

imagem_questao = st.file_uploader(
    "Imagem de Apoio (opcional)", 
    type=["png", "jpg", "jpeg"]
)

# Campos específicos para múltipla escolha
if st.session_state.tipo_questao == "Múltipla Escolha":
    st.markdown("**Opções de Resposta:**")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.opcoes["A"] = st.text_input("Opção A*", value=st.session_state.opcoes["A"])
        st.session_state.opcoes["C"] = st.text_input("Opção C*", value=st.session_state.opcoes["C"])
    with col2:
        st.session_state.opcoes["B"] = st.text_input("Opção B*", value=st.session_state.opcoes["B"])
        st.session_state.opcoes["D"] = st.text_input("Opção D*", value=st.session_state.opcoes["D"])

# Botões de ação
col_salvar, col_limpar = st.columns(2)
with col_salvar:
    if st.button("💾 Salvar Questão", use_container_width=True):
        if not texto_questao.strip():
            st.error("O texto da questão é obrigatório!")
        elif st.session_state.tipo_questao == "Múltipla Escolha" and any(not opcao.strip() for opcao in st.session_state.opcoes.values()):
            st.error("Preencha todas as opções de múltipla escolha!")
        else:
            nova_questao = {
                "texto": texto_questao,
                "tipo": st.session_state.tipo_questao,
                "imagem": imagem_questao.read() if imagem_questao else None,
                "opcoes": st.session_state.opcoes.copy() if st.session_state.tipo_questao == "Múltipla Escolha" else None
            }
            
            if st.session_state.editando_index is not None:
                st.session_state.questoes[st.session_state.editando_index] = nova_questao
                st.success("Questão atualizada com sucesso!")
                st.session_state.editando_index = None
            else:
                st.session_state.questoes.append(nova_questao)
                st.success("Questão adicionada com sucesso!")
            
            # Reset dos campos
            st.session_state.texto_questao = ""
            st.session_state.opcoes = {"A": "", "B": "", "C": "", "D": ""}
            st.rerun()

with col_limpar:
    if st.button("♻️ Limpar Campos", use_container_width=True):
        st.session_state.texto_questao = ""
        st.session_state.opcoes = {"A": "", "B": "", "C": "", "D": ""}
        st.session_state.editando_index = None
        st.rerun()

# --- Lista de Questões ---
st.subheader("📚 Questões Adicionadas")
st.caption(f"Total: {len(st.session_state.questoes)} questões")

if not st.session_state.questoes:
    st.info("Nenhuma questão adicionada ainda. Use o editor acima para começar.")
else:
    for idx, questao in enumerate(st.session_state.questoes):
        with st.expander(f"Questão {idx + 1}: {questao['texto'][:50]}...", expanded=False):
            # ... (código de exibição mantido)

            if st.button("✏️ Editar", key=f"edit_{idx}"):
                st.session_state.editando_index = idx
                st.session_state.texto_questao = questao["texto"]
                st.session_state.tipo_questao = questao["tipo"]
                if questao["opcoes"]:
                    st.session_state.opcoes = questao["opcoes"].copy()
                st.rerun()
            
            if st.button("🗑️ Excluir", key=f"del_{idx}"):
                st.session_state.questoes.pop(idx)
                st.success("Questão removida!")
                st.rerun()

# --- Exportação ---
st.subheader("📤 Exportar Prova")
if st.button("💾 Gerar Documento Word", use_container_width=True):
    if not st.session_state.questoes:
        st.error("Adicione pelo menos uma questão antes de exportar!")
    else:
        # ... (código de exportação mantido)
