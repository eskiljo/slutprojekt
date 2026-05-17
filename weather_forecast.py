import requests
import json
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)

forecast_info = "./forecast.txt"

base_url = "https://api.open-meteo.com/v1/forecast"



def get_forecast(lat, long, parameters, days):
    url = "https://api.open-meteo.com/v1/forecast"
    global data

    params = {}
    params["latitude"] = lat
    params["longitude"] = long
    params["forecast_days"] = days
    
    parameter_keys = parameters.keys()

    print(parameters)
    print(parameter_keys)

    for parameter in parameter_keys:
        if "hourly" in parameter:
            key = parameter.split("-")[1]
            if params["hourly"]:
                params["hourly"] += "," + key
            else:
                params["hourly"] = key
        else:
            if params["daily"]:
                params["daily"] += "," + parameter
            else:
                params["daily"] = parameter
            #lägg till att systemet sparar vilka som hör ihop, så att grafen innehåller dem tillsammans 
            



    #params = {  "latitude": 59.33,
    #    "longitude": 18.07,
    #    "hourly": "temperature_2m,relative_humidity_2m",
    #    "daily": "temperature_2m_mean",
    #    "forecast_days": 5 #days
    #}
    response = requests.get(url, params=params)
    data = response.json()


    #with open("forecast.txt") as forecast_info:
        #text = json.load(forecast_info)
        #global data
        #if not text:
            #with open("forecast.txt", "w") as forecast_info:
                #url = "https://api.open-meteo.com/v1/forecast"
                
                #params = {  "latitude": 59.33,
                #            "longitude": 18.07,
                #            "hourly": "temperature_2m,relative_humidity_2m",
                #            "daily": "temperature_2m_mean",
                #            "forecast_days": 5 #days
               # }
              #  response = requests.get(url, params=params)
             #   data = response.json()
           #     forecast_info.write(json.dumps(data))
      #  else:
      #      data = text
    #print(data)

def get_geolocation(name):
    search_url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    response = requests.get(search_url, params=params)
    geolocation_data = response.json()
    return geolocation_data


def plot_graphs():
    #print(data["hourly"])
    plt.subplot(2, 1, 1)
    plt.plot(data["hourly"]["temperature_2m"], color = "red")
    plt.xlabel("Temperature")
    plt.ylabel("C°")

    plt.subplot(2, 1, 2)
    plt.plot(data["hourly"]["relative_humidity_2m"], color = "blue")
    plt.xlabel("Humidity")
    plt.ylabel("%")

    #detta är FEL, använd flera grafer och klistra sedan ihop dem till en stor png som användaren kollar på (alternativt en hemsida)
    #plt.show()
    plt.tight_layout()
    plt.savefig("forecast.png")

@app.route("/")
def home():
    return render_template("selection.html")


@app.route("/request_form", methods=["POST"])
def get_request():
    position = {}
    requested_data = request.form.to_dict()
    for key in ["city", "lat", "long"]:
        if key in requested_data:
            position[key] = requested_data.pop(key)
    #print(position)
    #print(requested_data)
    if position["city"]:
        coordinates = get_geolocation(position["city"])
        print(coordinates)
        get_forecast(coordinates["results"][0]["latitude"], coordinates["results"][0]["longitude"], requested_data, request.form["forecast_days"])
    elif position["lat"] and position["long"]:
        get_forecast(position["lat"], position["long"], requested_data, request.form["forecast_days"])
    else:
        return render_template("selection.html")
    return render_template("weather.html")


#get_forecast()

if __name__ == "__main__":
    app.run(debug=True)

#status_code