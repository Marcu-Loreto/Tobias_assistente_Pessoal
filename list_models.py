import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Listando modelos do Google disponíveis para a sua API Key:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f" -> {m.name}")
