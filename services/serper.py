import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search_serper(query):
    url = "https://google.serper.dev/search"
    payload = {
        "q": query,
        "num": 5
    }
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error calling Serper: {response.status_code}")
        return None
    
def get_prospect_signals(name, company, role):
    queries = [
        f'"{name}" "{role}" "{company}" linkedin',
        f'"{company}" funding OR "Series A" OR "Series B" 2025 OR 2026',
        f'"{name}" interview OR podcast OR keynote 2025 OR 2026',
        f'"{company}" product launch OR announcement 2025 OR 2026'
    ]
    
    all_results = []
    for q in queries:
        res = search_serper(q)
        if res:
            organic = res.get('organic', [])
            for item in organic:
                all_results.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet'),
                    "date": item.get('date'),
                    "query": q # Track which query found this
                })
    return all_results, queries
