import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

# Inicialização segura da session_state
if 'questoes' not in st.session_state:
    st.session_state.questoes = []

# --- FUNÇÕES AUXILIARES ---
def criar_pasta_temp():
    """Cria pasta temporária para armazenar imagens"""
    if not os.path.exists("temp"):
        os.makedirs("temp")

def limpar_pasta_temp():
    """Remove arquivos temporários após uso"""
    if os.path.exists("temp"):
        for file in os.listdir("temp"):
            os.remove(os.path.join("temp", file))

# --- FORMULÁRIO PRINCIPAL ---
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

# --- ADIÇÃO DE QUESTÕES ---
st.subheader("✍️ Adicionar Questões")

tipo_questao = st.radio("Tipo de questão:", ["Dissertativa", "Múltipla Escolha"], horizontal=True)
nova_questao = st.text_area("Texto da questão", height=100)
imagem_questao = st.file_uploader("Imagem para a questão (opcional)", type=["png", "jpg", "jpeg"])

if tipo_questao == "Múltipla Escolha":
    col1, col2 = st.columns(2)
    with col1:
        opcao_a = st.text_input("Opção A")
        opcao_b = st.text_input("Opção B")
    with col2:
        opcao_c = st.text_input("Opção C")
        opcao_d = st.text_input("Opção D")
    resposta_correta = st.selectbox("Resposta correta:", ["A", "B", "C", "D"])

if st.button("➕ Adicionar Questão"):
    if nova_questao.strip():
        questao_data = {
            "texto": nova_questao,
            "tipo": tipo_questao,
            "imagem": None,
            "opcoes": {
                "A": opcao_a if tipo_questao == "Múltipla Escolha" else "",
                "B": opcao_b if tipo_questao == "Múltipla Escolha" else "",
                "C": opcao_c if tipo_questao == "Múltipla Escolha" else "",
                "D": opcao_d if tipo_questao == "Múltipla Escolha" else ""
            },
            "resposta": resposta_correta if tipo_questao == "Múltipla Escolha" else None
        }
        
        if imagem_questao:
            criar_pasta_temp()
            imagem_path = os.path.join("temp", imagem_questao.name)
            with open(imagem_path, "wb") as f:
                f.write(imagem_questao.getbuffer())
            questao_data["imagem"] = imagem_path
        
        st.session_state.questoes.append(questao_data)
        st.success("Questão adicionada com sucesso!")
    else:
        st.warning("Por favor, insira o texto da questão.")

# --- VISUALIZAÇÃO DAS QUESTÕES ---
st.subheader("📋 Questões da Prova")

if not st.session_state.questoes:
    st.info("Nenhuma questão adicionada ainda.")
else:
    for i, questao in enumerate(st.session_state.questoes, 1):
        # Verificação segura da estrutura da questão
        if not isinstance(questao, dict) or "texto" not in questao:
            st.error(f"Estrutura inválida na questão {i}")
            continue
            
        st.markdown(f"### Questão {i}")
        st.write(questao.get("texto", "Texto não disponível"))
        
        if questao.get("imagem"):
            try:
                st.image(questao["imagem"], width=400)
            except Exception as e:
                st.error(f"Erro ao carregar imagem: {str(e)}")
        
        if questao.get("tipo") == "Múltipla Escolha":
            st.markdown("**Opções:**")
            cols = st.columns(2)
            with cols[0]:
                st.write(f"**A)** {questao['opcoes'].get('A', '')}")
                st.write(f"**B)** {questao['opcoes'].get('B', '')}")
            with cols[1]:
                st.write(f"**C)** {questao['opcoes'].get('C', '')}")
                st.write(f"**D)** {questao['opcoes'].get('D', '')}")
            st.write(f"**Resposta correta:** {questao.get('resposta', '')}")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✏️ Editar Questão {i}", key=f"edit_{i}"):
                pass  # Implementar lógica de edição
        with col2:
            if st.button(f"❌ Remover Questão {i}", key=f"del_{i}"):
                st.session_state.questoes.pop(i-1)
                st.experimental_rerun()
        st.markdown("---")

# --- GERAR DOCUMENTO WORD ---
st.subheader("📤 Gerar Prova em Word")

if st.button("🖨️ Gerar Documento"):
    if not st.session_state.questoes:
        st.error("Adicione pelo menos uma questão!")
    else:
        try:
            doc = Document()
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)
            
            # Adicionar questões ao documento
            for i, questao in enumerate(st.session_state.questoes, 1):
                if not isinstance(questao, dict):
                    continue
                    
                doc.add_paragraph(f"{i}. {questao.get('texto', '')}")
                
                if questao.get("imagem"):
                    try:
                        doc.add_picture(questao["imagem"], width=Inches(4.5))
                        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    except Exception as e:
                        st.error(f"Erro na imagem da questão {i}: {str(e)}")
                
                if questao.get("tipo") == "Múltipla Escolha":
                    for letra in ['A', 'B', 'C', 'D']:
                        doc.add_paragraph(f"{letra}) {questao['opcoes'].get(letra, '')}")
                    doc.add_paragraph(f"Resposta correta: {questao.get('resposta', '')}")
                
                doc.add_paragraph()
            
            nome_arquivo = f"Prova_{disciplina}_{serie.replace(' ', '_')}.docx"
            doc.save(nome_arquivo)
            
            with open(nome_arquivo, "rb") as f:
                st.download_button(
                    "⬇️ Baixar Prova",
                    f,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            st.success("Documento gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao gerar documento: {str(e)}")
