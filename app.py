from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form.get("city")
        zipcode = request.form.get("zipcode")

        # Weather API setup
        api_key = "89d42c2da09aa7b892d4568bfad8e366"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{zipcode}&appid={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temp_c = round(data['main']['temp'] - 273.15, 2)  # Kelvin to Celsius
            temp_f = round((temp_c * 9/5) + 32, 2)  # Celsius to Fahrenheit
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            humidity = data["main"]["humidity"]

            # Determine clothing and accessory recommendations
            clothing, accessories, sunscreen = get_recommendations(temp_c, description, wind_speed)

            weather = {
                "location": data["name"],
                "temperature": f"{temp_c}°C / {temp_f}°F",
                "description": description,
                "humidity": f"{humidity}%",
                "wind_speed": f"{wind_speed} m/s",
                "clothing": clothing,
                "accessories": accessories,
                "sunscreen": sunscreen
            }
            return render_template("index.html", weather=weather)
        else:
            error = "Could not retrieve weather data. Please try again."
            return render_template("index.html", error=error)

    return render_template("index.html")

def get_recommendations(temp, description, wind_speed):
    clothing = ""
    accessories = ""
    sunscreen = ""

    if temp > 30:
        clothing = "Wear light, breathable clothing like shorts and a t-shirt."
        accessories = "Sunglasses 🕶️, a sun hat 👒, and a water bottle 💧."
        sunscreen = "Apply sunscreen 🧴 before going out."
    elif 20 <= temp <= 30:
        clothing = "Wear comfortable clothes like jeans and a t-shirt."
        accessories = "A cap 🧢 and sunglasses 🕶️ would be good."
    elif 10 <= temp < 20:
        clothing = "Wear a light jacket 🧥 or sweater."
        accessories = "A scarf 🧣 and closed shoes 👞 are recommended."
    elif 0 <= temp < 10:
        clothing = "Wear a heavy coat 🧥, sweater, and thermal clothing."
        accessories = "Gloves 🧤, a beanie 🎩, and a scarf 🧣."
    else:
        clothing = "Wear thermal layers, a heavy winter coat, and thick pants."
        accessories = "Winter boots 🥾, gloves 🧤, a beanie 🎩, and a scarf 🧣."

    if "rain" in description:
        accessories += " Don't forget an umbrella ☔ and a waterproof jacket! 🧥"
    elif "snow" in description:
        accessories += " Wear snow boots ❄️ and a warm hat 🧢."
    elif "clear" in description and temp > 20:
        sunscreen = "Apply sunscreen 🧴 before heading out."

    if wind_speed > 5:
        accessories += " It's windy, consider a windbreaker or a sturdy hat. 🌬️"

    return clothing, accessories, sunscreen

if __name__ == "__main__":
    app.run(debug=True)
