from langchain_core.tools import tool
import re

@tool
def validate_data(data: str, data_type: str) -> str:
    """Ferramenta de validação de estrutura e conformidade analítica.
    Verifica se uma string pertence a um formato válido.
    Formatos suportados (data_type): 'email', 'cpf' (básico estrutural), 'url'.
    """
    data = data.strip()
    dt = data_type.lower()
    
    if dt == "email":
        return "Válido" if re.match(r"[^@]+@[^@]+\.[^@]+", data) else "Inválido: O formato de e-mail está incorreto."
    elif dt == "url":
        if not data.startswith(("http://", "https://")):
            return "Inválido: A URL não começa com http:// ou https://."
        try:
            import urllib.request
            req = urllib.request.Request(data, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() < 400:
                    return f"Válido e Acessível: URL respondeu corretamente."
                return f"Inválido: O servidor da página retornou o código HTTP {response.getcode()}."
        except Exception as e:
            return f"Link Quebrado/Inacessível: Não foi possível acessar a URL informada (Erro: {str(e)})."
    elif dt == "cpf":
        # Validação estrutural len
        cpf_clean = re.sub(r"\D", "", data)
        if len(cpf_clean) == 11:
            return "Válido estruturalmente (11 dígitos inteiros)."
        return "Inválido: CPF não contém 11 números."
    else:
        return f"Erro: Tipo de dado '{data_type}' não suportado pelo validator.py."
