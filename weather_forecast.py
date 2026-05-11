import requests
import json
import matplotlib.pyplot as plt

base_url = "https://api.open-meteo.com/v1/forecast"

def get_forecast():
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {  "latitude": 59.33,
                "longitude": 18.07,
                "hourly": "temperature_2m,relative_humidity_2m",
                "forecast_days": 2
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    print(data["hourly"])

get_forecast()

#status_code