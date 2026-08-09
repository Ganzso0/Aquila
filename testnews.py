import requests

api_key = "2dd136a436c563b3916d4c5031190665"

url = "https://gnews.io/api/v4/search"

params = {
    "apikey": api_key,
    "q": "NVIDIA",
    "lang": "es",
    "max": 5
}

response = requests.get(url, params=params)

print("STATUS:", response.status_code)
print("RESPUESTA:", response.text)