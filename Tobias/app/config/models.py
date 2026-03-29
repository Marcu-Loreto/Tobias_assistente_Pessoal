import os

# Definição de fallback models caso o .env não os forneça
MODEL_OPENAI_STRONG = os.getenv("MODEL_OPENAI_STRONG", "gpt-4o")
MODEL_OPENAI_BALANCED = os.getenv("MODEL_OPENAI_BALANCED", "gpt-4o-mini")
MODEL_GOOGLE_BALANCED = os.getenv("MODEL_GOOGLE_BALANCED", "gemini-2.5-flash")
MODEL_GOOGLE_CHEAP = os.getenv("MODEL_GOOGLE_CHEAP", "gemini-2.5-flash-lite")
