import requests
from bs4 import BeautifulSoup

def handle_web_search(assistant, entities):
    query = " ".join(entities.get("tokens", []))
    if not query:
        return "I'm sorry, I need a search query."
    
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_result = soup.find('div', class_='BNeawe').text
        return f"Here's what I found: {search_result}"
    except:
        return f"I'm sorry, I couldn't perform a web search for '{query}'."
