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

# ... (código anterior permanece igual até a seção de exportação)

# --- Exportação ---
st.subheader("📤 Exportar Prova")
if st.button("💾 Gerar Documento Word", use_container_width=True):
    if not st.session_state.questoes:
        st.error("Adicione pelo menos uma questão antes de exportar!")
    elif not all([nome_professor, disciplina, serie, bimestre]):
        st.error("Preencha todos os campos obrigatórios nos dados da prova!")
    else:
        try:
            doc = Document()
            
            # Configuração do estilo
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)
            
            # Cabeçalho com logo
            if logo_escola:
                logo_escola.seek(0)
                doc.add_picture(logo_escola, width=Inches(1.5))
                last_paragraph = doc.paragraphs[-1] 
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Informações da prova
            if nome_escola:
                escola_para = doc.add_paragraph(nome_escola)
                escola_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                escola_para.runs[0].bold = True
            
            titulo = doc.add_paragraph(f"PROVA DE {disciplina.upper()} - {bimestre.upper()}")
            titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            titulo.runs[0].bold = True
            
            doc.add_paragraph(f"Professor: {nome_professor}")
            doc.add_paragraph(f"Turma: {serie}")
            doc.add_paragraph(f"Data: {data_prova.strftime('%d/%m/%Y')}")
            doc.add_paragraph("\n")
            
            # Adicionar questões
            for idx, questao in enumerate(st.session_state.questoes, 1):
                # Enunciado
                para = doc.add_paragraph()
                para.add_run(f"{idx}. ").bold = True
                para.add_run(questao["texto"])
                
                # Imagem (se houver)
                if questao["imagem"]:
                    try:
                        doc.add_picture(BytesIO(questao["imagem"]), width=Inches(4.5))
                        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    except:
                        doc.add_paragraph("[Erro ao carregar imagem]")
                
                # Opções (se for múltipla escolha)
                if questao["tipo"] == "Múltipla Escolha":
                    for letra, texto in questao["opcoes"].items():
                        doc.add_paragraph(f"{letra}) {texto}")
                else:
                    for _ in range(3):  # Linhas para resposta
                        doc.add_paragraph("_" * 60)
                
                doc.add_paragraph()  # Espaço entre questões
            
            # Gerar arquivo
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            nome_arquivo = f"Prova_{disciplina}_{serie}_{bimestre}.docx".replace(" ", "_")
            st.download_button(
                "⬇️ Baixar Prova em Word",
                data=buffer,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao gerar documento: {str(e)}")
