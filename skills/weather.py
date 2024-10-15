import requests

def handle_weather(assistant, entities):
    location = entities.get("location", "")
    time = entities.get("time", "current")
    
    if not location:
        return "I'm sorry, I need a location to check the weather."
    
    base_url = f"https://wttr.in/{location}?format=j1"
    
    try:
        response = requests.get(base_url)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        description = current['weatherDesc'][0]['value']
        
        if time.lower() == "current":
            return f"The current weather in {location} is {description} with a temperature of {temp}°C."
        else:
            # You can add logic here to handle future weather forecasts
            return f"The weather in {location} for {time} is expected to be {description} with a temperature around {temp}°C."
    except:
        return f"I'm sorry, I couldn't fetch the weather for {location}."
