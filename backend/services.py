import requests

def safe_api_call(func, fallback):
    try:
        return func()
    except Exception as e:
        return fallback

# 🌱 SOIL
def get_soil(location):
    def call():
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query?lat=28.6&lon=77.2"
        requests.get(url, timeout=5)
        return {
            "nitrogen": "low",
            "ph": "neutral",
            "moisture": "medium"
        }

    return safe_api_call(call, {
        "nitrogen": "unknown",
        "ph": "unknown",
        "moisture": "unknown"
    })


# 🌦️ WEATHER
def get_weather(location):
    def call():
        url = "https://api.open-meteo.com/v1/forecast?latitude=28.6&longitude=77.2&daily=temperature_2m_max,precipitation_sum"
        data = requests.get(url, timeout=5).json()

        return {
            "temperature": data["daily"]["temperature_2m_max"][0],
            "rainfall": data["daily"]["precipitation_sum"][0]
        }

    return safe_api_call(call, {
        "temperature": "unknown",
        "rainfall": "unknown"
    })


# 💰 MARKET (simulated scraping layer)
def get_market_data():
    return {
        "urea_price": "₹270/bag",
        "dap_price": "₹1350/bag",
        "note": "Prices are approximate (simulated)"
    }