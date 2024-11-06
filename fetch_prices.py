import requests
import sqlite3
from datetime import datetime, timedelta

# API URL
API_URL = "https://isot.okte.sk/api/v1/dam/results"

# Funkcia na načítanie cien z API s dátumovým rozsahom
def fetch_prices(date_from, date_to):
    try:
        response = requests.get(API_URL, params={
            "deliveryDayFrom": date_from,
            "deliveryDayTo": date_to
        })
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Chyba pri načítavaní dát z API: {e}")
        return None

# Funkcia na uloženie cien do databázy
def save_prices_to_db(data):
    connection = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = connection.cursor()

    for entry in data:
        date = entry['deliveryDay']      # Používame 'deliveryDay' namiesto 'date'
        hour = entry['period']           # Používame 'period' na určenie hodiny
        price = entry['price']           # Používame 'price' pre cenu

        cursor.execute('''
            INSERT INTO prices (date, hour, price) VALUES (?, ?, ?)
        ''', (date, hour, price))

    connection.commit()
    connection.close()
    print("Ceny boli úspešne uložené do databázy.")

# Hlavný skript
if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")  # Dnešný dátum
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")  # Zajtrajší dátum
    prices_data = fetch_prices(today, tomorrow)

    # Výpis dát na kontrolu
    if prices_data:
        print("Dáta z API:", prices_data)  # Výpis na kontrolu obsahu
        save_prices_to_db(prices_data)
