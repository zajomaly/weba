import requests
import sqlite3
from datetime import datetime, timedelta

def fetch_tomorrow_data():
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()

    # Nastav dátum zajtrajška
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # Skontroluj, či už ceny na zajtra existujú
    cursor.execute("SELECT * FROM prices WHERE date = ?", (tomorrow,))
    data = cursor.fetchall()

    # Ak ceny nie sú v databáze, načítaj ich z API
    if not data:
        url = f"https://isot.okte.sk/api/v1/dam/results?deliveryDayFrom={tomorrow}&deliveryDayTo={tomorrow}"
        response = requests.get(url)
        if response.status_code == 200:
            new_data = response.json()
            for entry in new_data:
                date = entry['deliveryDay']
                hour = entry['period']
                price = entry['price']
                cursor.execute("INSERT INTO prices (date, hour, price) VALUES (?, ?, ?)", (date, hour, price))
            conn.commit()
            print("Nové údaje pre zajtrajšok boli úspešne načítané.")
        else:
            print("Údaje zatiaľ nie sú dostupné. Skúsime znova o hodinu.")
    else:
        print("Údaje na zajtrajší deň už sú dostupné.")

    conn.close()

if __name__ == "__main__":
    fetch_tomorrow_data()
