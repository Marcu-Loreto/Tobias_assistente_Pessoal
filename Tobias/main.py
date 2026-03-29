"""
main.py — Interface Streamlit do Agente Tobias
Responsabilidade única: UI, gerenciamento de sessão e invocação do grafo.
"""

import streamlit as st
import os
from dotenv import load_dotenv

# OBRIGATÓRIO: Carregar variávies de ambiente ANTES de instanciar memórias
load_dotenv()

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from core.utils import get_system_prompt, load_relatorio_skill, verify_and_scrub_links
from core.document_parser import parse_uploaded_file
from core.graph import graph, AgentState
from core.memory import redis_memory, qdrant_memory
from app.router.model_selector import select_model

# Validação de chave de API
import os

api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------------------------------
# Configuração da Página (deve ser a primeira chamada st.)
# -------------------------------------------------------
st.set_page_config(
    page_title="Agente Tobias",
    page_icon="🤖",
    layout="wide",
)

# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.title("🤖 Agente Tobias")
st.markdown(
    "Assistente pessoal crítico e assertivo — com pesquisa na web, "
    "calculadora, validação de dados e relatórios no estilo **C-Level**."
)

if not api_key:
    st.error(
        "⚠️ `OPENAI_API_KEY` não encontrada no `.env`. Adicione sua chave para continuar."
    )
    st.stop()

# -------------------------------------------------------
# Estado de Sessão
# -------------------------------------------------------
if "session_id" not in st.session_state:
    import uuid

    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id

# Carrega histórico do Redis (se disponível), senão usa lista local vazia
if "messages" not in st.session_state:
    st.session_state.messages = redis_memory.load(session_id)

# -------------------------------------------------------
# Sidebar — Upload de Documentos
# -------------------------------------------------------
with st.sidebar:
    st.header("📂 Gerenciador de Arquivos")
    st.caption("Faça upload de documentos para análise contextual.")
    uploaded_files = st.file_uploader(
        label="Selecione um ou mais arquivos",
        type=["pdf", "docx", "txt", "csv", "xlsx"],
        accept_multiple_files=True,
        key="file_uploader",
    )
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")

    st.divider()
    if redis_memory.available:
        st.success("⚡ Memória Rápida: Redis ativo")
    else:
        st.warning("⚡ Memória Rápida: Redis offline")
    if qdrant_memory.available:
        st.success("🧠 Memória Semântica: Qdrant ativo")
    else:
        st.warning("🧠 Memória Semântica: Qdrant offline")

    col1, col2 = st.columns(2)
    if col1.button(
        "🗑️ Limpar Redis",
        use_container_width=True,
        help="Apaga o histórico conversacional atual.",
    ):
        if redis_memory.available:
            redis_memory.clear(session_id)
        st.session_state.messages = []
        st.rerun()

    if col2.button(
        "🗑️ Limpar Qdrant",
        use_container_width=True,
        help="Deleta a coleção inteira e vetoriza do zero.",
    ):
        if qdrant_memory.available:
            qdrant_memory.reset_collection()
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "**Skills Ativas:** 🔍 Web Search Avançada | 🧮 Calculadora | 🛡️ Segurança | 📄 Relatórios C-Level"
    )

# -------------------------------------------------------
# Renderizar Histórico de Mensagens
# -------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------------
# Lógica de Input e Invocação do Grafo
# -------------------------------------------------------
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    # Exibe a mensagem do usuário imediatamente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Extrai conteúdo dos arquivos carregados
    document_context = ""
    if uploaded_files:
        document_context = "\n--- INÍCIO DOS DOCUMENTOS FORNECIDOS ---\n"
        for uf in uploaded_files:
            text = parse_uploaded_file(uf)
            document_context += f"**Arquivo:** {uf.name}\n{text}\n{'=' * 30}\n"
            uf.seek(0)  # Reseta o ponteiro para reutilização
        document_context += "--- FIM DOS DOCUMENTOS FORNECIDOS ---\n"

    # Detecta se é uma solicitação de relatório
    trigger_words = [
        "relatório",
        "relatorio",
        "análise",
        "analise",
        "documento",
        "dataset",
        "dados",
        "report",
    ]
    is_report_request = (
        any(word in prompt.lower() for word in trigger_words) or len(uploaded_files) > 0
    )

    # Detecta se possui intenção clara de pesquisa profunda na web
    search_trigger_words = [
        "pesquise",
        "pesquisa",
        "busque na web",
        "investigue",
        "dossiê",
        "buscar",
        "pesquisar",
    ]
    is_search_request = any(word in prompt.lower() for word in search_trigger_words)

    # Avaliação dinâmica de roteamento de IA baseada na complexidade
    model_id = select_model(
        prompt=prompt,
        is_report_request=is_report_request,
        is_search_request=is_search_request,
        has_documents=bool(document_context),
    )

    # Monta o input final (prompt + contexto de documentos)
    final_input = prompt
    if document_context:
        final_input += (
            "\n\nAnalise o(s) documento(s) abaixo com base no meu pedido:\n"
            + document_context
        )

    # Constrói a lista de mensagens LangChain a partir do histórico
    SYSTEM_PROMPT = get_system_prompt()
    api_messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in st.session_state.messages[:-1]:  # histórico sem o prompt atual
        if msg["role"] == "user":
            api_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            api_messages.append(AIMessage(content=msg["content"]))

    api_messages.append(HumanMessage(content=final_input))

    # Estado inicial para o LangGraph
    initial_state: AgentState = {
        "user_input": prompt,
        "document_context": document_context,
        "language": "pt",
        "is_admin": False,
        "admin_validated": False,
        "is_report_request": is_report_request,
        "is_search_request": is_search_request,
        "selected_llm": model_id,
        "messages": api_messages,
        "response": "",
    }

    # Invoca o grafo e exibe a resposta
    with st.spinner(f"⚙️ Processando I.A via {model_id}..."):
        final_state = graph.invoke(initial_state)

        # Modo manutenção retorna em `response`, modo normal na lista messages
        if final_state.get("admin_validated"):
            bot_response = final_state.get("response", "")
        else:
            messages = final_state.get("messages", [])
            bot_response = ""
            for msg in reversed(messages):
                if hasattr(msg, "type") and msg.type == "ai":
                    content = msg.content
                    if isinstance(content, str) and content.strip():
                        bot_response = content
                        break
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_val = item.get("text", "")
                                if text_val.strip():
                                    bot_response = text_val
                                    break
                        if bot_response:
                            break

        # Pós-processamento de segurança (Anti-Alucinação de Links)
        # Varre a resposta do modelo atrás de URLs e frita tudo que for 404 antes do usuário ver
        bot_response = verify_and_scrub_links(bot_response)

    with st.chat_message("assistant"):
        st.markdown(bot_response)

    # Persiste no histórico local da sessão
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Salva histórico atualizado no Redis (memória rápida)
    redis_memory.save(session_id, st.session_state.messages)

    # Arquiva par pergunta-resposta no Qdrant (memória semântica de longo prazo)
    qdrant_memory.store(
        user_input=prompt,
        assistant_response=bot_response,
        metadata={"session_id": session_id, "had_documents": bool(document_context)},
    )
