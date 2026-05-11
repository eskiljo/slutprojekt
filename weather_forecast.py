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
    
    #print(data["hourly"])
    plt.plot(data["hourly"]["temperature_2m"], color = "red")
    plt.plot(data["hourly"]["relative_humidity_2m"], color = "blue")
    #detta är FEL, använd flera grafer och klistra sedan ihop dem till en stor png som användaren kollar på (alternativt en hemsida)
    plt.xlabel("Temperature (red) and Humidity (blue)")
    #plt.show()
    plt.tight_layout()
    plt.savefig("forecast.png")


get_forecast()

#status_code