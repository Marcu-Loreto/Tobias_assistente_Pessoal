from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm_client(model_id: str, temperature: float = 0.3) -> BaseChatModel:
    """
    Fábrica universal para retornar a instância LangChain do provedor correto
    baseado no model_id instanciado em modo dinâmico.
    """
    # Detecção se é OpenAI (gpt, o1, o3, etc) ou Google (gemini)
    if "gpt" in model_id.lower() or "o1" in model_id.lower() or "o3" in model_id.lower():
        # Utiliza OPENAI_API_KEY do ambiente automaticamente
        return ChatOpenAI(model=model_id, temperature=temperature)
        
    elif "gemini" in model_id.lower():
        # Utiliza GOOGLE_API_KEY do ambiente automaticamente
        return ChatGoogleGenerativeAI(model=model_id, temperature=temperature)
        
    else:
        # Fallback de segurança para OpenAI
        return ChatOpenAI(model=model_id, temperature=temperature)
