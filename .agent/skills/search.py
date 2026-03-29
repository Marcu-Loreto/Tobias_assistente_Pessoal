from langchain_core.tools import tool
from ddgs import DDGS

@tool
def search_internet(query: str) -> str:
    """Ferramenta essencial para consultar furos recentes, notícias ou fatos gerais da internet.
    Sempre a utilize se não tiver certeza de uma informação ou se for um fato do mundo real que precise de consulta externa.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "Nenhum resultado encontrado."
        return "\n\n".join([f"**Título:** {r['title']}\n**URL:** {r['href']}\n**Conteúdo:** {r['body']}" for r in results])
    except Exception as e:
        return f"Erro ao acessar mecanismo de busca: {str(e)}"
