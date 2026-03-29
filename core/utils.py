"""
core/utils.py
Funções utilitárias para carregamento de prompts e skills do agente.
"""

import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def is_url_active(url: str) -> bool:
    """Realiza um teste rápido se a URL retorna código 200-399. Retorna True para não conseguir verificar (assume válida por padrão)."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            code = response.getcode()
            return code < 400
    except urllib.error.HTTPError as e:
        return e.code >= 400
    except Exception:
        return True


def verify_and_scrub_links(text: str) -> str:
    """
    Encontra todas as URLs HTTP/HTTPS em um texto.
    Verifica a conectividade de cada uma simultaneamente.
    Substitui links quebrados/alucinados por um aviso amigável.
    """
    if not isinstance(text, str) or not text:
        return text

    urls = list(set(re.findall(r'https?://[^\s<>"\']+', text)))
    if not urls:
        return text

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(is_url_active, urls))

    for url, is_valid in zip(urls, results):
        if not is_valid:
            text = text.replace(url, "")

            markdown_link_pattern = re.compile(
                r"\[([^\]]*)\]\(" + re.escape(url) + r"\)"
            )
            text = markdown_link_pattern.sub(
                r"*⚠️ Link removido: URL inválida/Quebrada*", text
            )

    return text


def load_prompt(path: str) -> str:
    """Carrega um arquivo de prompt em texto. Fallback se não encontrar."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are Tobias, a helpful and assertive AI assistant."


def load_relatorio_skill() -> str:
    """Carrega a skill de relatórios C-Level do diretório .agent/skills."""
    skill_path = os.path.join(os.getcwd(), ".agent", "skills", "relatorios", "SKILL.md")
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Skill de relatórios não encontrada."


def load_pesquisa_skill() -> str:
    """Carrega a skill de pesquisa web profunda do diretório .agent/skills."""
    skill_path = os.path.join(
        os.getcwd(), ".agent", "skills", "pesquisa_web", "SKILL.md"
    )
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def get_system_prompt() -> str:
    """Retorna o prompt principal do sistema a partir de prompts/agente.md."""
    return load_prompt(os.path.join(os.getcwd(), "prompts", "agente.md"))
