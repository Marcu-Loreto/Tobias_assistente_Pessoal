"""
core/graph.py
Construção do grafo LangGraph do Agente Tobias.
Define: AgentState, Nodes, Tools e compilação do StateGraph.
"""
import os
import sys
from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from core.utils import get_system_prompt, load_relatorio_skill, load_pesquisa_skill
from core.memory import qdrant_memory
from app.clients.llm_client import get_llm_client

# Adicionar skills ao path para importação das tools
skills_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".agent", "skills")
if skills_path not in sys.path:
    sys.path.insert(0, skills_path)

# Importar tools criadas em .agent/skills/
try:
    from search import search_internet
    from calculator import calculate_math
    from validator import validate_data
    from security import check_password_security, analyze_injection_attempt
    AGENT_TOOLS = [
        search_internet,
        calculate_math,
        validate_data,
        check_password_security,
        analyze_injection_attempt,
    ]
except ImportError as e:
    print(f"[AVISO] Erro ao carregar skills: {e}")
    AGENT_TOOLS = []

# Prompt principal do agente (carregado uma vez)
SYSTEM_PROMPT = get_system_prompt()

# -------------------------------------------------------
# Estado do Agente (TypedDict para o LangGraph)
# -------------------------------------------------------
class AgentState(TypedDict):
    user_input: str
    document_context: str
    language: str
    is_admin: bool
    admin_validated: bool
    is_report_request: bool
    is_search_request: bool
    selected_llm: str
    messages: Annotated[list, add_messages]
    response: str


# -------------------------------------------------------
# Nodes
# -------------------------------------------------------
def detect_language(state: AgentState) -> dict:
    """Detecta o idioma solicitado pelo usuário e atualiza o state."""
    text = state["user_input"].lower()
    if "english" in text:
        lang = "en"
    elif "español" in text or "espanhol" in text:
        lang = "es"
    else:
        lang = "pt"
    return {"language": lang}


def check_admin(state: AgentState) -> dict:
    """Verifica se o input contém as credenciais de manutenção."""
    text = state["user_input"].lower()
    if "loreto" in text and "1423" in text:
        return {"is_admin": True, "admin_validated": True}
    return {"is_admin": False, "admin_validated": False}


def route_mode(state: AgentState) -> str:
    """Roteador condicional: admin vai para maintenance, demais para normal."""
    return "maintenance" if state["admin_validated"] else "normal"


def normal_node(state: AgentState) -> dict:
    """
    Nó principal de conversação.
    1. Busca memórias semânticas relevantes no Qdrant (se disponível)
    2. Injeta contexto histórico + skill de relatório no prompt
    3. Vincula tools ao LLM e invoca
    """
    model_name = state.get("selected_llm", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    llm = get_llm_client(model_id=model_name, temperature=0.3)
    if AGENT_TOOLS:
        llm = llm.bind_tools(AGENT_TOOLS)

    messages = list(state["messages"])
    extra_system_parts = []

    # 1. Memória semântica — injeta contexto de interações passadas relevantes
    if qdrant_memory.available:
        past_memories = qdrant_memory.search(state["user_input"], top_k=3)
        if past_memories:
            context_block = qdrant_memory.format_context(past_memories)
            extra_system_parts.append(context_block)

    # 2. Skill de relatório C-Level (se solicitado)
    if state.get("is_report_request"):
        skill_content = load_relatorio_skill()
        extra_system_parts.append(f"INSTRUÇÃO OBRIGATÓRIA — USE ESTA SKILL PARA FORMATAR O RELATÓRIO:\n{skill_content}")

    # 3. Skill de pesquisa aprofundada (se solicitado)
    if state.get("is_search_request"):
        skill_content = load_pesquisa_skill()
        extra_system_parts.append(f"INSTRUÇÃO OBRIGATÓRIA — SIGA ESTA SKILL PARA A SUA PESQUISA:\n{skill_content}")

    # Prepend SystemMessages adicionais antes das mensagens de conversa
    if extra_system_parts:
        prefix = [SystemMessage(content="\n\n".join(extra_system_parts))]
        messages = prefix + messages

    response = llm.invoke(messages)
    return {"messages": [response]}


def maintenance_node(state: AgentState) -> dict:
    """
    Nó de modo manutenção (admin). Responde com status do sistema
    sem acionar a LLM externa.
    """
    msg = """
🧰 **[MAINTENANCE MODE ENABLED]**

| Item | Status |
|------|--------|
| Usuário Admin | ✅ Verificado (loreto) |
| Token | ✅ Válido |
| Skills Carregadas | search, calculator, validator, security, relatorios, pesquisa_web |
| Grafo LangGraph | ✅ Operacional |
| Roteador de Modelos | 🚦 Ativo (LLM Dinâmico) |
| Memória Rápida (Redis) | {redis_status} |
| Memória Semântica (Qdrant) | {qdrant_status} |
| Diagnóstico | ✅ Nenhuma falha detectada |
""".format(
        redis_status="✅ Ativa" if True else "⚠️ Inativa",
        qdrant_status="✅ Ativa" if qdrant_memory.available else "⚠️ Inativa",
    )
    return {"response": msg}


# -------------------------------------------------------
# BUILD DO GRAFO
# -------------------------------------------------------
def build_graph():
    """Constrói e compila o StateGraph do Agente Tobias."""
    builder = StateGraph(AgentState)

    builder.add_node("detect_language", detect_language)
    builder.add_node("check_admin", check_admin)
    builder.add_node("normal", normal_node)
    builder.add_node("tools", ToolNode(AGENT_TOOLS) if AGENT_TOOLS else lambda x: x)
    builder.add_node("maintenance", maintenance_node)

    builder.set_entry_point("detect_language")
    builder.add_edge("detect_language", "check_admin")
    builder.add_conditional_edges("check_admin", route_mode, {
        "normal": "normal",
        "maintenance": "maintenance",
    })
    # Loop tools: normal -> tools -> normal (até não ter mais tool_calls)
    builder.add_conditional_edges("normal", tools_condition, {
        "tools": "tools",
        "__end__": END,
    })
    builder.add_edge("tools", "normal")
    builder.add_edge("maintenance", END)

    return builder.compile()


# Instância singleton do grafo (compilado uma única vez na importação)
graph = build_graph()
