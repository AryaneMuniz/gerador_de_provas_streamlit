import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Gerador de Provas", layout="centered")
st.title("📝 Gerador de Provas Escolares")

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

# --- UPLOAD DO LOGO ---
st.sidebar.markdown("### 🔳 Configurações do Cabeçalho")
logo_escola = st.sidebar.file_uploader(
    "Carregar logo da escola (opcional)",
    type=["png", "jpg", "jpeg"],
    key="logo_uploader"
)

# --- FORMULÁRIO PRINCIPAL ---
with st.form("dados_prova"):
    nome_professor = st.text_input("Nome do Professor")
    disciplina = st.text_input("Disciplina")
    serie = st.selectbox(
        "Série/Turma",
        options=[
            "1º ano - Ensino Fundamental", "2º ano - Ensino Fundamental", 
            "3º ano - Ensino Fundamental", "4º ano - Ensino Fundamental",
            "5º ano - Ensino Fundamental", "6º ano - Ensino Fundamental",
            "7º ano - Ensino Fundamental", "8º ano - Ensino Fundamental",
            "9º ano - Ensino Fundamental", "1º ano - Ensino Médio",
            "2º ano - Ensino Médio", "3º ano - Ensino Médio"
        ]
    )
    bimestre = st.selectbox(
        "Bimestre",
        options=["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"]
    )
    data_prova = st.date_input("Data da Prova", value=date.today())
    st.form_submit_button("Salvar Configurações")

# --- GERENCIAMENTO DE QUESTÕES ---
if "questoes" not in st.session_state:
    st.session_state.questoes = []

st.subheader("✍️ Adicionar Questões")

# Seleção do tipo de questão
tipo_questao = st.radio(
    "Tipo de questão:",
    options=["Dissertativa", "Múltipla Escolha"],
    horizontal=True
)

# Campos da questão
nova_questao = st.text_area("Texto da questão", height=100)

# Upload de imagem para questão
imagem_questao = st.file_uploader(
    "Imagem para a questão (opcional)",
    type=["png", "jpg", "jpeg"],
    key="imagem_questao"
)

# Campos para múltipla escolha
if tipo_questao == "Múltipla Escolha":
    col1, col2 = st.columns(2)
    with col1:
        opcao_a = st.text_input("Opção A", value="")
        opcao_b = st.text_input("Opção B", value="")
    with col2:
        opcao_c = st.text_input("Opção C", value="")
        opcao_d = st.text_input("Opção D", value="")
    resposta_correta = st.selectbox(
        "Resposta correta:",
        options=["A", "B", "C", "D"]
    )

# Botão para adicionar questão
if st.button("➕ Adicionar Questão"):
    if nova_questao.strip():
        questao_data = {
            "texto": nova_questao,
            "tipo": tipo_questao,
            "imagem": None,
            "opcoes": None if tipo_questao == "Dissertativa" else {
                "A": opcao_a,
                "B": opcao_b,
                "C": opcao_c,
                "D": opcao_d
            },
            "resposta": resposta_correta if tipo_questao == "Múltipla Escolha" else None
        }
        
        # Processar imagem se existir
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
        st.markdown(f"### Questão {i}")
        st.write(questao["texto"])
        
        # Mostrar imagem se existir
        if questao["imagem"]:
            st.image(questao["imagem"], width=400, caption=f"Imagem da Questão {i}")
        
        # Mostrar opções se for múltipla escolha
        if questao["tipo"] == "Múltipla Escolha":
            st.markdown("**Opções:**")
            cols = st.columns(2)
            with cols[0]:
                st.write(f"**A)** {questao['opcoes']['A']}")
                st.write(f"**B)** {questao['opcoes']['B']}")
            with cols[1]:
                st.write(f"**C)** {questao['opcoes']['C']}")
                st.write(f"**D)** {questao['opcoes']['D']}")
            st.write(f"**Resposta correta:** {questao['resposta']}")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✏️ Editar Questão {i}", key=f"edit_{i}"):
                # Lógica de edição (implementar conforme necessário)
                pass
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
        doc = Document()
        
        # Configuração do estilo
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)
        
        # Adicionar logo se existir
        if logo_escola:
            criar_pasta_temp()
            logo_path = os.path.join("temp", logo_escola.name)
            with open(logo_path, "wb") as f:
                f.write(logo_escola.getbuffer())
            doc.add_picture(logo_path, width=Inches(1.5))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()
        
        # Cabeçalho da prova
        cabecalho = doc.add_heading(level=1)
        cabecalho_run = cabecalho.add_run(f"PROVA DE {disciplina.upper()} - {bimestre.upper()}")
        cabecalho_run.bold = True
        cabecalho_run.font.size = Pt(14)
        cabecalho.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Informações da prova
        info = doc.add_paragraph()
        info.add_run(f"Professor: {nome_professor}\n")
        info.add_run(f"Turma: {serie}\n")
        info.add_run(f"Data: {data_prova.strftime('%d/%m/%Y')}\n\n")
        info.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Adicionar questões
        for i, questao in enumerate(st.session_state.questoes, 1):
            # Texto da questão
            p_questao = doc.add_paragraph()
            p_questao.add_run(f"{i}. {questao['texto']}").bold = True
            
            # Imagem da questão
            if questao["imagem"]:
                try:
                    doc.add_picture(
                        questao["imagem"],
                        width=Inches(4.5)  # Largura ajustável
                    )
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                except Exception as e:
                    st.error(f"Erro ao inserir imagem da Questão {i}: {str(e)}")
            
            # Opções (para múltipla escolha)
            if questao["tipo"] == "Múltipla Escolha":
                for letra, texto in questao["opcoes"].items():
                    doc.add_paragraph(f"{letra}) {texto}", style='ListBullet')
                doc.add_paragraph(f"Resposta correta: {questao['resposta']}")
            
            doc.add_paragraph()  # Espaço entre questões
        
        # Salvar documento
        nome_arquivo = f"Prova_{disciplina}_{serie.replace(' ', '_')}_{bimestre.replace(' ', '_')}.docx"
        doc.save(nome_arquivo)
        
        # Botão de download
        with open(nome_arquivo, "rb") as f:
            st.download_button(
                label="⬇️ Baixar Prova em Word",
                data=f,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        # Limpar arquivos temporários
        limpar_pasta_temp()
        st.success("Prova gerada com sucesso!")
