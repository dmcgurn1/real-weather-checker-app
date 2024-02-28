# Import packages
import requests
from dataclasses import dataclass
from flask import Flask, render_template, request
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import time
from dotenv import load_dotenv
import os

# Import API Keys from '.env'
load_dotenv()
GeoNamesUsername = os.getenv('GeoNamesUsername')
OpenWeatherAPIKey = os.getenv('OpenWeatherAPIKey')
MetOfficeAPIKey = os.getenv('MetOfficeAPIKey')

# Import modules
import conversions  # Module containing constants for common conversions e.g. M/S to MPH

# Functions
def validate_request(submitted_field):

    # Validate submitted form field
    submitted_field = submitted_field.replace(" ", "")

    if submitted_field.isalpha() and (1 < len(submitted_field) <= 30):
        valid_field_condition = True
    else:
        valid_field_condition = False

    return valid_field_condition

def geo_coder(town, country_code):

    api_search_url = f'http://api.geonames.org/searchJSON?q={town}&country={country_code}&featureClass=P&continentCode=&fuzzy=0.6&username={GeoNamesUsername}'

    # Validate submitted form fields for request (using helper function)
    if validate_request(town) is True and validate_request(country_code) is True:
        geonames_request = requests.get(api_search_url)
    else:
        return "Error"

    # Bad request
    if geonames_request.status_code == 401 or geonames_request.json()['totalResultsCount'] == 0:
        return "Error"  # Use this returned string "Error" later to redirect user

    # Store geocoding information
    name = geonames_request.json()['geonames'][0]['name']
    country_code = geonames_request.json()['geonames'][0]['countryCode']
    latitude = geonames_request.json()['geonames'][0]['lat']
    longitude = geonames_request.json()['geonames'][0]['lng']
    location_id = geonames_request.json()['geonames'][0]['geonameId']

    # GeoNames data
    geo_coder_data = {
        'name': name,
        'country_code': country_code,
        'latitude': latitude,
        'longitude': longitude,
        'location_id': location_id
    }

    return geo_coder_data


def bs4logic(url):

    # Make a request to url
    response = requests.get(url)

    # Parse webpage with Beautiful Soup
    soup = BeautifulSoup(response.content, "html.parser")

    return soup


def clean_data(variable):

    # Convert value to string
    variable = str(variable)

    # Remove any degree symbols, percentage signs, or spaces
    variable = variable.strip("°% ")

    # Convert into float
    variable = float(variable)

    return variable


def format_variable(variable):

    # Convert to float
    variable = float(variable)

    # Round float
    variable = round(variable, 1)

    # If the float is a whole number, convert it to an integer
    if variable % 1 == 0:
        variable = int(variable)

    # Convert variable into string for output
    variable = str(variable)

    return variable

# Weather emoji picker
def weather_emoji_picker(weather_desc):

    # HTMl Emojis start with '&#' followed by a number
    emoji_base = '&#'

    # HTML emoji codes mapped to weather description
    emoji_codes = {
        "Not available": "10068",
        "Clear night": "127747",
        "Sunny day": "127775",
        "Partly cloudy (night)": "9729",
        "Partly cloudy (day)": "9925",
        "Not used": "10068",
        "Mist": "127787;&#65039",
        "Fog": "127787;&#65039",
        "Cloudy": "9729;&#65039",
        "Overcast": "127745",
        "Light rain shower (night)": "9748",
        "Light rain shower (day)": "9748",
        "Drizzle": "9748",
        "Light rain": "9748",
        "Heavy rain shower (night)": "9748",
        "Heavy rain shower (day)": "9748",
        "Heavy rain": "9748",
        "Sleet shower (night)": "127784;&#65039",
        "Sleet shower (day)": "127784;&#65039",
        "Sleet": "127784;&#65039",
        "Hail shower (night)": "127784;&#65039",
        "Hail shower (day)": "127784;&#65039",
        "Hail": "127784;&#65039",
        "Light snow shower (night)": "127784;&#65039",
        "Light snow shower (day)": "127784;&#65039",
        "Light snow": "9731;&#65039",
        "Heavy snow shower (night)": "9731;&#65039",
        "Heavy snow shower (day)": "9731;&#65039",
        "Heavy snow": "9731;&#65039",
        "Thunder shower (night)": "127785;&#65039",
        "Thunder shower (day)": "127785;&#65039",
        "Thunder": "127785;&#65039"
    }

    weather_emoji = emoji_base + emoji_codes[weather_desc]

    return weather_emoji

# Weather image picker
def weather_image_picker(weather_desc):

    weather_image = ''

    # HTML code for image to be inserted in webpage mapped to weather descriptions
    weather_images_dict = {
        "Not available": '<img src="static/weatherimages/NotAvailable.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Clear night": '<img src="static/weatherimages/ClearNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Sunny day": '<img src="static/weatherimages/Sunny.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Partly cloudy (night)": '<img src="static/weatherimages/CloudyNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Partly cloudy (day)": '<img src="static/weatherimages/CloudyDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Not used": '<img src="static/weatherimages/NotAvailable.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Mist": '<img src="static/weatherimages/Mist.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Fog": '<img src="static/weatherimages/Fog.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Cloudy": '<img src="static/weatherimages/Cloudy.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Overcast": '<img src="static/weatherimages/Overcast.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Light rain shower (night)": '<img src="static/weatherimages/LightRainShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Light rain shower (day)": '<img src="static/weatherimages/LightRainShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Drizzle": '<img src="static/weatherimages/Drizzle.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Light rain": '<img src="static/weatherimages/LightRain.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Heavy rain shower (night)": '<img src="static/weatherimages/HeavyRainShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Heavy rain shower (day)": '<img src="static/weatherimages/HeavyRainShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Heavy rain": '<img src="static/weatherimages/HeavyRain.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Sleet shower (night)": '<img src="static/weatherimages/SleetShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Sleet shower (day)": '<img src="static/weatherimages/SleetShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Sleet": '<img src="static/weatherimages/Sleet.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Hail shower (night)": '<img src="static/weatherimages/HailShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Hail shower (day)": '<img src="static/weatherimages/HailShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Hail": '<img src="static/weatherimages/Hail.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Light snow shower (night)": '<img src="static/weatherimages/LightSnowShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Light snow shower (day)": '<img src="static/weatherimages/LightSnowShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Light snow": '<img src="static/weatherimages/LightSnow.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Heavy snow shower (night)": '<img src="static/weatherimages/HeavySnowShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Heavy snow shower (day)": '<img src="static/weatherimages/HeavySnowShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Heavy snow": '<img src="static/weatherimages/HeavySnow.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Thunder shower (night)": '<img src="static/weatherimages/ThunderShowerNight.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Thunder shower (day)": '<img src="static/weatherimages/ThunderShowerDay.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
        "Thunder": '<img src="static/weatherimages/Thunder.jpg" style="transform: translate(100px,10px)" alt="Weather Image";>',
    }

    weather_image = weather_images_dict[weather_desc]

    return weather_image


# Main Logic:
# -----------

# Get weather information from:
# 1. OpenWeather
# 2. Met Office
# 3. BBC Weather (+Sunrise/Sunset)
# 4. Yr.No

# Additional:
# TimeandDate.com - 'timeanddate.com/moon/phases' (Moon Phase)

# -------------------

# OpenWeather:

def OpenWeather(latitude, longitude):

    base_url = 'https://api.openweathermap.org/data/2.5/weather'

    query_url = f"{base_url}?lat={latitude}&lon={longitude}&units=metric&APPID={OpenWeatherAPIKey}"

    # Request
    ow_request = requests.get(query_url)

    # Check if the request is ok (HTTP status code within 200-299)
    if ow_request.ok is False:
        raise Exception("OpenWeather API received a bad request.")

    # Data
    data = ow_request.json()

    temperature = data['main']['temp']
    feels_like = data['main']['feels_like']
    wind_speed = data['wind']['speed'] * conversions.MS_TO_MPH
    weather_desc = data['weather'][0]['description']
    humidity = data['main']['humidity']

    # Open Weather data
    ow_data = {
        'temperature': temperature,
        'feels_like': feels_like,
        'wind_speed': wind_speed,
        'weather_desc': weather_desc,
        'humidity': humidity
    }

    return ow_data

# -------------------

# Met Office:

def MetOffice(latitude, longitude):

    base_url = 'https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/'

    # Met Office weather parameters
    requestHeaders = {"apikey": f'{MetOfficeAPIKey}'}
    headers = {'accept': "application/json"}
    headers.update(requestHeaders)
    params = {
        'excludeParameterMetadata': False,
        'includeLocationName': True,
        'latitude': latitude,
        'longitude': longitude
    }

    timesteps = 'hourly'

    url = base_url + timesteps

    req = requests.get(url, headers=headers, params=params)

    # Check if the request is ok (HTTP status code within 200-299)
    if req.ok is False:
        raise Exception("MetOffice Weather API received a bad request.")

    # Convert current time into a string that will match in the json data
    current_time = str(datetime.date(datetime.now())) + str('T') + str(datetime.time(datetime.now()))[0:3] + str('00Z')

    # Retrieve data
    json_key = req.json()['features'][0]['properties']['timeSeries']

    # 24 hours in a day
    for i in range(25):

        # Check for current date and time in data
        if json_key[i]['time'] == current_time:

            # Temperature
            temperature = json_key[i]['screenTemperature']

            # Feels like
            feels_like = json_key[i]['feelsLikeTemperature']

            # Wind speed
            wind_speed = json_key[i]['windSpeed10m']

            # Gust speed
            gust_speed = json_key[i]['windGustSpeed10m'] * conversions.KN_TO_MPH

            # Rain chance
            rain_chance = json_key[i]['probOfPrecipitation']

            # Snow

            # Snow condition flag: 0 = Not going to snow, 1 = Forecasted to snow
            snow_condition_flag = 0

            # Snow amount - doesn't always exist in the json data
            try:
                snow_amount = json_key[i]['totalSnowAmount']
            except:
                snow_amount = 0

            # Set snow condition flag equal to 1 if snow is forecasted
            if snow_amount > 0:
                snow_condition_flag = 1

            # Significant weather codes
            significant_weather_codes = {
                "NA": "Not available",
                "0": "Clear night",
                "1": "Sunny day",
                "2": "Partly cloudy (night)",
                "3": "Partly cloudy (day)",
                "4": "Not used",
                "5": "Mist",
                "6": "Fog",
                "7": "Cloudy",
                "8": "Overcast",
                "9": "Light rain shower (night)",
                "10": "Light rain shower (day)",
                "11": "Drizzle",
                "12": "Light rain",
                "13": "Heavy rain shower (night)",
                "14": "Heavy rain shower (day)",
                "15": "Heavy rain",
                "16": "Sleet shower (night)",
                "17": "Sleet shower (day)",
                "18": "Sleet",
                "19": "Hail shower (night)",
                "20": "Hail shower (day)",
                "21": "Hail",
                "22": "Light snow shower (night)",
                "23": "Light snow shower (day)",
                "24": "Light snow",
                "25": "Heavy snow shower (night)",
                "26": "Heavy snow shower (day)",
                "27": "Heavy snow",
                "28": "Thunder shower (night)",
                "29": "Thunder shower (day)",
                "30": "Thunder"
            }

            # Significant weather code
            weather_code = json_key[i]['significantWeatherCode']
            weather_code = str(weather_code)

            # Getting value for significant weather code key
            weather_desc = significant_weather_codes[weather_code]

            # UV index
            uv_index_codes = {
                "0": "Low exposure. No protection required. You can safely stay outside",
                "1": "Low exposure. No protection required. You can safely stay outside",
                "2": "Low exposure. No protection required. You can safely stay outside",
                "3": "Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen",
                "4": "Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen",
                "5": "Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen",
                "6": "High exposure. Seek shade during midday hours, cover up and wear sunscreen",
                "7": "High exposure. Seek shade during midday hours, cover up and wear sunscreen",
                "8": "Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential",
                "9": "Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential",
                "10": "Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential",
                "11": "Extreme. Avoid being outside during midday hours. Shirt, sunscreen and hat essential."
            }

            uv_index_code = json_key[i]['uvIndex']

            # If UV Index > 11 display the highest warning
            if int(uv_index_code) > 11:
                uv_index_desc = "Extreme. Avoid being outside during midday hours. Shirt, sunscreen and hat essential."

            # Otherwise display the corresponding description for the index number
            else:
                uv_index_desc = str(uv_index_code)
                uv_index_desc = uv_index_codes[uv_index_desc]

            # Humidity
            humidity = json_key[i]['screenRelativeHumidity']

            # Met Office weather data
            mo_data = {
                'temperature': temperature,
                'feels_like': feels_like,
                'wind_speed': wind_speed,
                'gust_speed': gust_speed,
                'weather_desc': weather_desc,
                'rain_chance': rain_chance,
                'snow_condition_flag': snow_condition_flag,
                'snow_amount': snow_amount,
                'uv_index_code': uv_index_code,
                'uv_index_desc': uv_index_desc,
                'humidity': humidity
            }

            return mo_data


# -------------------

# BBC Weather:

def BBCWeather(location_id):

    base_url = 'https://bbc.co.uk/weather/'

    forecast_url = f'{base_url}{location_id}'

    # Using helper function
    soup = bs4logic(forecast_url)

    # Temperature:
    temperature = soup.find("div", {"class": "wr-time-slot-primary__temperature"}).get_text()
    temperature = temperature[0:2]

    # Feels like:
    feels_like = soup.find("span", {"class": "wr-time-slot-secondary__feels-like-temperature-value gel-long-primer-bold wr-value--temperature--c"}).get_text()

    # Wind speed:
    wind_speed = soup.find("div", {"class": "wr-time-slot-primary__wind-speed"}).get_text().strip('Wind speed mph').split()[0]

    # Wind description:
    wind_desc = soup.find("div", {"class": "wr-time-slot-secondary__wind-direction wr-time-slot-secondary__bottom-section gel-long-primer"}).get_text()

    # Rain chance:
    rain_chance = soup.find("div", {"class": "wr-u-font-weight-500"}).get_text()
    rain_chance = rain_chance.replace('chance of precipitation', '')

    # Sunrise:
    sunrise = soup.find("span", {"class": "wr-c-astro-data__sunrise gel-pica-bold gs-u-pl-"}).get_text()
    sunrise = sunrise.strip('Sunrise')

    # Sunset:
    sunset = soup.find("span", {"class": "wr-c-astro-data__sunset gel-pica gs-u-pl-"}).get_text()
    sunset = sunset.strip('Sunset')

    # Humidity:
    humidity = soup.find("dd", {"class": "wr-time-slot-secondary__value gel-long-primer-bold"}).get_text()

    # BBC Weather data
    bbc_data = {
        'temperature': temperature,
        'feels_like': feels_like,
        'wind_speed': wind_speed,
        'wind_desc': wind_desc,
        'rain_chance': rain_chance,
        'humidity': humidity,
        'sunrise': sunrise,
        'sunset': sunset
    }

    return bbc_data

# -------------------

# Yr.No:

def YrNo(location_id):

    base_url = 'https://www.yr.no/en/forecast/daily-table/2-'

    forecast_url = f'{base_url}{location_id}'

    # Using helper function
    soup = bs4logic(forecast_url)

    # Temperature - temperature can be warm or cold:
    try:
        temperature = soup.find("span", {"class": "temperature temperature--warm"}).get_text()
    except:
        temperature = soup.find("span", {"class": "temperature temperature--cold"}).get_text()

    temperature = temperature.split('Temperature')[1]

    # Feels like:
    feels_like = soup.find("div", {"class": "feels-like-text"}).get_text()
    feels_like = feels_like.split('Feels like ')[1]
    feels_like = feels_like[-3:]

    # Wind speed:
    wind_speed = soup.find("span", {"class": "wind__value now-hero__next-hour-wind-value"}).get_text()
    wind_speed = float(wind_speed) * conversions.MS_TO_MPH

    # Rainfall:
    rain_amount = soup.find("span", {"class": "now-hero__next-hour-precipitation-value"}).get_text()

    # YrNo weather data
    yrno_data = {
        'temperature': temperature,
        'feels_like': feels_like,
        'wind_speed': wind_speed,
        'rain_amount': rain_amount
    }

    return yrno_data

# -------------------

# TimeandDate.com Moon Phase:

def Moon_Phase(location_id):

    # Get moon phase for chosen location
    url = f'https://www.timeanddate.com/moon/phases/@{location_id}'

    # Helper function
    soup = bs4logic(url)

    # Moon phase tonight
    moon_phase = soup.find_all("td")[1].get_text()

    moon_percent = soup.find("span", {"id": "cur-moon-percent"}).get_text()

    # HTML moon emoji code strings all start the same, just the last 2 characters are different for specific moon phase
    moon_emoji_base = '&#1277'

    moon_emoji_dict = {
        "New Moon": "61",
        "Waxing Crescent": "62",
        "First Quarter": "63",
        "Waxing Gibbous": "64",
        "Full Moon": "65",
        "Waning Gibbous": "66",
        "Third Quarter": "67",
        "Waning Crescent": "68"
    }

    # Retrieve last 2 characters of moon emoji code mapped to moon phase
    last_2_characters = moon_emoji_dict[moon_phase]

    # Concatenate strings to create moon_emoji
    moon_emoji = moon_emoji_base + last_2_characters

    # TimeandDate.com moon phase dataa
    moon_data = {
        'moon_phase': moon_phase,
        'moon_emoji': moon_emoji,
        'moon_percent': moon_percent
    }

    return moon_data


# Initialise output data class
@dataclass
class AppData:
    current_date: str
    current_time: str
    latitude: str
    longitude: str
    location_name: str
    location_id: str
    temperature: str
    feels_like: str
    weather_desc: str
    wind_speed: str
    gust_speed: str
    wind_desc: str
    rain_chance: str
    rain_amount: str
    snow_condition_flag: int
    snow_amount: str
    uv_index_code: str
    uv_index_desc: str
    humidity: str
    sunrise: str
    sunset: str
    moon_phase: str
    moon_emoji: str
    moon_percent: str
    weather_emoji: str
    weather_image: str


# Flask website
app = Flask(__name__)

# Home
@app.route('/')
def home():

    return render_template('home.html')

# Results
@app.route('/', methods=['POST'])
def results():

    time.sleep(0.1)

    # Initialise weather_data variable
    weather_data = None

    # Create empty numpy arrays to put variables in, to average afterwards
    all_temperatures = np.array([])
    all_feels_like = np.array([])
    all_wind_speeds = np.array([])
    all_rain_chance = np.array([])
    all_humidity = np.array([])

    # Geocoding information

    # Get town and country code from html form submission
    town = request.form['townName']
    country_code = request.form['countryCode']

    # Redirect 'home_error.html' if bad request
    if geo_coder(town, country_code) == "Error":

        return render_template('home_error.html')

    # Store location info from geo_coder function in variable
    GEO_CODER_DATA = geo_coder(town, country_code)

    # Get location info using geo_coder function
    latitude = GEO_CODER_DATA['latitude']
    longitude = GEO_CODER_DATA['longitude']
    location_id = GEO_CODER_DATA['location_id']

    # Getting weather information...

    # Get weather data
    OW_DATA = OpenWeather(latitude, longitude)
    MO_DATA = MetOffice(latitude, longitude)
    BBC_DATA = BBCWeather(location_id)
    YRNO_DATA = YrNo(location_id)
    MOON_DATA = Moon_Phase(location_id)

    # Print weather data:
    print('OpenWeather Data:', OW_DATA)
    print('MetOffice Data:', MO_DATA)
    print('BBC Data:', BBC_DATA)
    print('YrNo Data:', YRNO_DATA)
    print('Moon Phase Data:', MOON_DATA)

    # Clean / store variables for averaging
    all_temperatures = np.append(all_temperatures, [
        clean_data(OW_DATA['temperature']),
        clean_data(MO_DATA['temperature']),
        clean_data(BBC_DATA['temperature']),
        clean_data(YRNO_DATA['temperature']),
    ])

    all_feels_like = np.append(all_feels_like, [
        clean_data(OW_DATA['feels_like']),
        clean_data(MO_DATA['feels_like']),
        clean_data(BBC_DATA['feels_like']),
        clean_data(YRNO_DATA['feels_like']),
    ])

    all_wind_speeds = np.append(all_wind_speeds, [
        clean_data(OW_DATA['wind_speed']),
        clean_data(MO_DATA['wind_speed']),
        clean_data(BBC_DATA['wind_speed']),
        clean_data(YRNO_DATA['wind_speed']),
    ])

    all_rain_chance = np.append(all_rain_chance, [
        clean_data(MO_DATA['rain_chance']),
        clean_data(BBC_DATA['rain_chance']),
    ])

    all_humidity = np.append(all_humidity, [
        clean_data(OW_DATA['humidity']),
        clean_data(MO_DATA['humidity']),
        clean_data(BBC_DATA['humidity'])
    ])

    # Print arrays
    print("All temperatures:", all_temperatures)
    print("All feels like:", all_feels_like)
    print("All wind speeds:", all_wind_speeds)
    print("All rain chance:", all_rain_chance)
    print("All humidity:", all_humidity)

    # Get average values from arrays
    average_temperature = np.average(all_temperatures)
    average_feels_like = np.average(all_feels_like)
    average_wind_speed = np.average(all_wind_speeds)
    average_rain_chance = np.average(all_rain_chance)
    average_humidity = np.average(all_humidity)

    # Format averages
    average_temperature = format_variable(average_temperature)
    average_feels_like = format_variable(average_feels_like)
    average_wind_speed = format_variable(average_wind_speed)
    average_rain_chance = format_variable(average_rain_chance)
    average_humidity = format_variable(average_humidity)

    # Store other variables
    weather_desc = MO_DATA['weather_desc']
    gust_speed = MO_DATA['gust_speed']
    wind_desc = BBC_DATA['wind_desc']
    rain_amount = YRNO_DATA['rain_amount']
    snow_condition_flag = MO_DATA['snow_condition_flag']
    snow_amount = MO_DATA['snow_amount']
    uv_index_code = MO_DATA['uv_index_code']
    uv_index_desc = MO_DATA['uv_index_desc']
    sunrise = BBC_DATA['sunrise']
    sunset = BBC_DATA['sunset']
    moon_phase = MOON_DATA['moon_phase']
    moon_percent = MOON_DATA['moon_percent']

    # Format other variables where necessary
    location_id = str(location_id)
    gust_speed = format_variable(gust_speed)
    snow_amount = format_variable(snow_amount)
    uv_index_code = format_variable(uv_index_code)
    moon_percent = format_variable(clean_data(moon_percent))

    # Extras:

    # Retrieve town and country code as shown in GeoNames API request, then format to create location_name string
    town = geo_coder(town, country_code)['name']
    country_code = geo_coder(town, country_code)['country_code']

    location_name = f'{town}, {country_code}'

    # Get date and time for current run
    current_date_str = f'{str(datetime.now())[8:10]}/{str(datetime.now())[5:7]}/{str(datetime.now())[0:4]}'
    current_time_str = f'{str(datetime.now())[11:16]}'

    # Weather emoji
    weather_emoji = weather_emoji_picker(weather_desc)

    # Weather image
    weather_image = weather_image_picker(weather_desc)

    # Moon emoji
    moon_emoji = MOON_DATA['moon_emoji']

    # Put output variable in AppData dataclass as 'weather_data'
    weather_data = AppData(
        current_date=current_date_str,
        current_time=current_time_str,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        location_id=location_id,
        temperature=average_temperature,
        feels_like=average_feels_like,
        weather_desc=weather_desc,
        wind_speed=average_wind_speed,
        gust_speed=gust_speed,
        wind_desc=wind_desc,
        rain_chance=average_rain_chance,
        rain_amount=rain_amount,
        snow_condition_flag=snow_condition_flag,
        snow_amount=snow_amount,
        uv_index_code=uv_index_code,
        uv_index_desc=uv_index_desc,
        humidity=average_humidity,
        sunrise=sunrise,
        sunset=sunset,
        moon_phase=moon_phase,
        moon_emoji=moon_emoji,
        moon_percent=moon_percent,
        weather_emoji=weather_emoji,
        weather_image=weather_image
    )

    # (Contains 23 variables)

    # Print weather_data, putting a new line after bracket/comma
    print(str(weather_data).replace('(', '(\n').replace("',", ",\n"))

    # Render results page
    return render_template('/results.html', output_data=weather_data)


if __name__ == '__main__':
    app.run(debug=True)
