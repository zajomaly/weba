import sqlite3
from datetime import datetime, timedelta
import numpy as np

def get_predicted_prices():
    # Predikcia cien na pozajtra
    predicted_prices = [(hour, round(90 + np.random.rand() * 50, 2)) for hour in range(1, 25)]
    return predicted_prices

def save_predicted_prices(predicted_prices, date):
    conn = sqlite3.connect('arbitrage.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predicted_prices WHERE date = ?", (date,))
    for hour, price in predicted_prices:
        cursor.execute("INSERT INTO predicted_prices (date, hour, price) VALUES (?, ?, ?)", (date, hour, price))
    conn.commit()
    conn.close()

# Získanie dátumu pozajtra
future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
predicted_prices = get_predicted_prices()
save_predicted_prices(predicted_prices, future_date)
print(f"Predikované ceny na {future_date} boli úspešne uložené.")
