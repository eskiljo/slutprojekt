import requests
import json
import os
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import subprocess


app = Flask(__name__)

forecast_info = "./forecast.txt"

base_url = "https://api.open-meteo.com/v1/forecast"


def get_forecast(lat, long, parameters, days):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {}
    if (-90 < lat < 90) and (-180 < long < 180):
        params["latitude"] = lat
        params["longitude"] = long
    else:
        return render_template("selection.html", error = "Error in coordinates")
    
    if days:
        params["forecast_days"] = days
    else:
        return render_template("selection.html", error = "Error in requested forecast length")
    
    parameter_keys = parameters.keys()

    joint_params = []

    for parameter in parameter_keys:
        if parameter == "forecast_days":
            pass
        elif "hourly" in parameter:
            key = parameter.split("-")[1]
            if params.get("hourly"):
                params["hourly"] += "," + key
            else:
                params["hourly"] = key
        else:
            if params.get("daily"):
                params["daily"] += "," + parameter
            else:
                params["daily"] = parameter
        if "," in parameter:
            #Adds parameters that were meant to be displayed in the same graph to a list
            joint_params.append(parameter) 
            
    response = requests.get(url, params=params)
    data = response.json()
    return queue_plot_graphs(data, joint_params)


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
    if len(geolocation_data) < 2:
        return False
    else:
        return geolocation_data


def queue_plot_graphs(data, joint_params): 
    subprocess.run("git clean -fd static", shell=True)
    open("static/.gitkeep", "a").close()
    subprocess.run(["git", "add", "static/"])
    subprocess.run(["git", "commit", "-m", "Empty static folder (remove untracked files)"])
    subprocess.run(["git", "push"])

    #break

    if data.get("hourly"):
        hourly = data["hourly"]
    else:
        #print("NO HOURLY")
        hourly = []
    
    if data.get("daily"):
        daily = data["daily"]
    else:
        #print("NO DAILY")
        daily = []
    

    used = set()

    for group in joint_params:
        isdaily = False
        ishourly = False
        params = group.split(",")
        graph = []
        
        for param in params:
            if param in daily:
                graph.append([param, daily[param]])
                used.add(param)
                isdaily = True

            elif param in hourly:
                graph.append([param, hourly[param]])
                used.add(param)
                ishourly = True

        if isdaily:
            graph.append(["time",daily["time"]])

        elif ishourly:
            graph.append(["time", hourly["time"]])

        plot_graph(graph, data, isdaily, ishourly)

    if daily:
        for i in daily:
            if i != "time":
                if not i in used:
                    plot_graph([["time", daily["time"]], [i, daily[i]]], data, True, False)
    if hourly:
        for i in hourly:
            if i != "time":
                if not i in used:
                    plot_graph([["time", hourly["time"]], [i, hourly[i]]], data, False, True)
    return send_images()



def plot_graph(list, data, isdaily, ishourly):
    plt.figure()
    colors = ["red", "blue", "green", "yellow"]
    times = 0
    title = []
    title_text = ""


    for item in list:
        if item[0] == "time":
            time = item[1]

    for item in list:

        if item[0] == "time":
            pass
        else: 
            if len(list) > 2:
                plt.plot(time, item[1], color = colors[times])
                times += 1
                title.append([item[0], colors[times]])
            else:
                plt.plot(time, item[1])
                title.append([item[0], ""])
        if isdaily:
            plt.ylabel(data["daily_units"][item[0]])
        elif ishourly:
            plt.ylabel(data["hourly_units"][item[0]])
    if title:
        for thing in title:
            if thing[1]:
                title_text += thing[0] + "(" + thing[1] + ")" + "\n"
            else:
                title_text += thing[0]
        plt.title(title_text)
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(16))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    global total_graphs
    total_graphs += 1
    plt.savefig("static/forecast" + str(total_graphs) + ".png")

def send_images():
    images = []
    file_path = "static"
    for filename in os.listdir(file_path):
        images.append(filename)
    return render_template("weather.html", images = images)


@app.route("/")
def home():
    return render_template("selection.html", error = "")


@app.route("/request_form", methods=["POST"])
def get_request():
    global total_graphs
    total_graphs = 0

    position = {}
    requested_data = request.form.to_dict()
    for key in ["city", "lat", "long"]:
        if key in requested_data:
            position[key] = requested_data.pop(key)

    if position["city"]:
        coordinates = get_geolocation(position["city"])

        if coordinates and coordinates["results"]:
            return get_forecast(coordinates["results"][0]["latitude"], coordinates["results"][0]["longitude"], requested_data, request.form["forecast_days"])
        else: 
            return render_template("selection.html", error = "Try again")

    elif position["lat"] and position["long"]:
        return get_forecast(position["lat"], position["long"], requested_data, request.form["forecast_days"])

    else:
        return render_template("selection.html", error = "Try again")
    


if __name__ == "__main__":
    app.run(debug=True)
