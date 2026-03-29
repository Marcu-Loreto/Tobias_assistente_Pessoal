import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from core.graph import AGENT_TOOLS, get_system_prompt

print("Iniciando bateria de testes Gemini...")
modelos = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
for m in modelos:
    print(f"\n--- Testando modelo: {m} ---")
    try:
        llm = ChatGoogleGenerativeAI(model=m, temperature=0.3)
        print(" [OK] Instancia do Langchain criada")
        llm_with_tools = llm.bind_tools(AGENT_TOOLS)
        print(" [OK] Tools vinculadas (bind_tools)")
        
        response = llm_with_tools.invoke("Olá, pode buscar no google como está o clima?")
        print(" [OK] Resposta obtida sem crash:", response.content[:30])
    except Exception as e:
        print(f" [ERRO FATAL] {e}")
