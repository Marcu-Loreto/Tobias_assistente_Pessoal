from langchain_core.tools import tool

@tool
def calculate_math(expression: str) -> str:
    """Calculadora matemática segura do Agente.
    Sempre use esta ferramenta para quaisquer contas (adição, subtração, multiplicação, divisão ou complexas) e estimativas com números reais ao invés de calcular mentalmente.
    Aceita strings com expressões matemáticas como '2 + 2 * 4' ou '100 / 3.5'.
    """
    try:
        # Avaliação de forma segura evitando evals complexos demais, filtrando só math
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Erro: Expressão matemática contém caracteres inválidos/não seguros."
            
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Erro ao calcular expressão matemática: {str(e)}"
