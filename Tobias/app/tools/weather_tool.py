"""
app/tools/weather_tool.py
Tool de previsão do tempo usando OpenWeatherMap API.
"""

import os
from langchain_core.tools import tool
import httpx


@tool
def get_weather(cidade: str) -> str:
    """
    Retorna a previsão do tempo para uma cidade específica.

    Args:
        cidade: Nome da cidade (ex: "São Paulo, BR" ou "London, UK")

    Returns:
        String com temperatura, descrição e detalhes do clima.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Erro: OPENWEATHER_API_KEY não configurada no .env"

    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {"q": cidade, "limit": 1, "appid": api_key}

    try:
        with httpx.Client() as client:
            geo_response = client.get(geo_url, params=params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data:
                return f"Cidade não encontrada: {cidade}"

            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
            nome_cidade = geo_data[0]["name"]
            pais = geo_data[0].get("country", "")

            weather_url = "https://api.openweathermap.org/data/2.5/weather"
            weather_params = {
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric",
                "lang": "pt_br",
            }

            weather_response = client.get(
                weather_url, params=weather_params, timeout=10
            )
            weather_response.raise_for_status()
            dados = weather_response.json()

            temp = dados["main"]["temp"]
            desc = dados["weather"][0]["description"]
            feels_like = dados["main"]["feels_like"]
            humidity = dados["main"]["humidity"]
            wind = dados["wind"]["speed"]

            return f"""
🌤️ **{nome_cidade}, {pais}**

• Temperatura: {temp}°C
• Sensação térmica: {feels_like}°C
• Umidade: {humidity}%
• Vento: {wind} m/s
• Clima: {desc.capitalize()}
"""

    except httpx.HTTPStatusError as e:
        return f"Erro HTTP ao buscar dados: {e.response.status_code}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
