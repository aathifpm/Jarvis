import requests

def handle_weather(assistant, entities):
    try:
        # Get the current IP address
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip_address = ip_response.json()['ip']

        # Get location based on IP
        location_response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        location_data = location_response.json()
        city = location_data.get('city', 'Unknown')
        country = location_data.get('country_name', 'Unknown')

        # Get weather data
        base_url = f"https://wttr.in/{city}?format=j1"
        weather_response = requests.get(base_url)
        weather_data = weather_response.json()
        current = weather_data['current_condition'][0]
        temp = current['temp_C']
        description = current['weatherDesc'][0]['value']

        return f"The current weather in {city}, {country} is {description} with a temperature of {temp}°C."
    except Exception as e:
        return f"I'm sorry, I couldn't fetch the weather information. Error: {str(e)}"
