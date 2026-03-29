from app.config.models import (
    MODEL_OPENAI_STRONG,
    MODEL_OPENAI_BALANCED,
    MODEL_GOOGLE_BALANCED,
    MODEL_GOOGLE_CHEAP,
)


def select_model(
    prompt: str, is_report_request: bool, is_search_request: bool, has_documents: bool
) -> str:

    prompt_lower = prompt.lower()
    words_count = len(prompt.split())

    # =========================
    # NÍVEL 1 — ALTA COMPLEXIDADE
    # =========================
    if is_report_request or is_search_request:
        return MODEL_OPENAI_STRONG

    strong_triggers = [
        "código",
        "debug",
        "erro",
        "analise",
        "análise",
        "arquitetura",
        "valide",
        "validação",
        "estratégia",
        "planeje",
        "passo a passo",
    ]

    if any(trigger in prompt_lower for trigger in strong_triggers):
        return MODEL_OPENAI_STRONG

    # =========================
    # 🟡 NÍVEL 1.5 — COMPLEXIDADE MÉDIA (IMPORTANTE)
    # =========================
    if words_count > 80 or has_documents:
        return MODEL_OPENAI_BALANCED

    # =========================
    # NÍVEL 3 — BARATO
    # =========================
    cheap_triggers = [
        "oi",
        "olá",
        "bom dia",
        "boa noite",
        "resuma",
        "traduza",
        "corrija frase",
        "me diga",
        "obrigado",
        "valeu",
    ]

    if words_count <= 5 and not has_documents:
        return MODEL_OPENAI_BALANCED

    if any(trigger in prompt_lower for trigger in cheap_triggers) and not has_documents:
        return MODEL_OPENAI_BALANCED

    # =========================
    # NÍVEL 2 — INTERMEDIÁRIO
    # =========================
    return MODEL_OPENAI_BALANCED
