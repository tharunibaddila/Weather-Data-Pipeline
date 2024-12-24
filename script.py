import requests
import pyodbc
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="weather_data_log.log",  # Log file
    filemode="a",  # Append to the existing log file
)

# Define a list of cities
cities = ["New York", "Los Angeles", "Houston", "London", "Tokyo", "Paris", "Mumbai", "Madanapalle", "Springfield"]

# Fetch weather data from OpenWeatherMap API for each city
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        logging.info(f"Successfully fetched data for {city}")
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPError for {city}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error for {city}: {e}")
        return None

# Load data into MSSQL
def load_to_mssql(df, server, database, username, password):
    try:
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
        
        for index, row in df.iterrows():
            cursor.execute("""
                INSERT INTO WeatherData (City, Country, Latitude, Longitude, TempCelsius, TempFahrenheit, Humidity, WindSpeedKph, RecordedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row['City'], row['Country'], row['Latitude'], row['Longitude'], row['TempCelsius'], row['TempFahrenheit'], row['Humidity'], row['WindSpeedKph'], row['RecordedAt'])
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Successfully loaded data into MSSQL")
    except Exception as e:
        logging.error(f"Error loading data into MSSQL: {e}")

# Define API key
api_key = "89d42c2da09aa7b892d4568bfad8e366"

# Store the weather data for all cities
all_data = []

# Iterate over each city
for city in cities:
    data = get_weather_data(city, api_key)
    if data:
        processed_data = {
            "City": data['name'],
            "Country": data['sys']['country'],
            "Latitude": data['coord']['lat'],
            "Longitude": data['coord']['lon'],
            "TempCelsius": data['main']['temp'] - 273.15,
            "TempFahrenheit": (data['main']['temp'] - 273.15) * 9/5 + 32,
            "Humidity": data['main']['humidity'],
            "WindSpeedKph": data['wind']['speed'] * 3.6,
            "RecordedAt": datetime.now()  # Add timestamp
        }
        all_data.append(processed_data)

# Check if any data was collected before attempting to load
if all_data:
    # Convert the collected data to a DataFrame
    df = pd.DataFrame(all_data)

    # Load the data to MSSQL
    load_to_mssql(df, 'MIDHTECH-01\\THARUNI', 'weather', 'weatheruser1', 'weather_user')
else:
    logging.warning("No data was collected from the API.")

