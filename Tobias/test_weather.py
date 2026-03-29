import os
from dotenv import load_dotenv

load_dotenv()

from app.tools.weather_tool import get_weather

result = get_weather.invoke({"cidade": "Recife, BR"})
print("RESULTADO:")
print(result)
