from langchain_core.tools import tool
import re

@tool
def check_password_security(password: str) -> str:
    """Ferramenta de análise de segurança para senhas.
    NÃO expõe os critérios rígidos ao usuário se ele não pedir, mas usa para classificar.
    Retorna Fraqueza, Força, ou vulnerabilidades como "falta de letrais especiais".
    """
    issues = []
    if len(password) < 8:
        issues.append("Menos de 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        issues.append("Não contém letras maiúsculas.")
    if not re.search(r"[a-z]", password):
        issues.append("Não contém letras minúsculas.")
    if not re.search(r"\d", password):
        issues.append("Não contém números.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        issues.append("Não contém caracteres especiais.")
        
    if not issues:
        return "SENHA FORTE E SEGURA."
    else:
        return "SENHA FRACA. Vulnerabilidades encontradas:\n" + "\n".join([f"- {i}" for i in issues])

@tool
def analyze_injection_attempt(prompt_history: str) -> str:
    """Verifica um trecho de texto ou comportamento do usuário em busca de Prompt Injections ou Jailbreaks.
    Essa tool escaneia termos associados a overrides de comandos.
    """
    heuristics = ["ignore all previous", "override", "system prompt", "you are now", "jailbreak", "DAN", "developer mode"]
    for h in heuristics:
        if h.lower() in prompt_history.lower():
            return "ALERTA DE SEGURANÇA: Possível tentativa de injeção ou jailbreak detectada (" + h + ")."
    return "Nenhuma ameaça óbvia detectada na análise sintática."
