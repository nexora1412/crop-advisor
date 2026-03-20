import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_weather(city: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "metric"
    }
    
    try:
        data = requests.get(url, params=params).json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall_mm": data.get("rain", {}).get("1h", 0),
            "condition": data["weather"][0]["description"]
        }
    except Exception as e:
        return {
            "temperature": "N/A",
            "humidity": "N/A", 
            "rainfall_mm": 0,
            "condition": "Unable to fetch weather"
        }