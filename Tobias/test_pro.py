import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from core.graph import AGENT_TOOLS

try:
    print("Testando gemini-pro-latest...")
    llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", temperature=0.3)
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    response = llm_with_tools.invoke("calcule 2 + 2")
    print("Sucesso!")
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("\nTestando gemini-2.5-flash...")
    llm2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    llm_with_tools2 = llm2.bind_tools(AGENT_TOOLS)
    response2 = llm_with_tools2.invoke("calcule 2 + 2")
    print("Sucesso!")
except Exception as e:
    import traceback
    traceback.print_exc()
