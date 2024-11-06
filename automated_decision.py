import sqlite3
from datetime import datetime
from app import calculate_thresholds, get_prices  # Importujeme funkcie z app.py

def automated_decision():
    # Získame prahové hodnoty pre nákup a predaj
    buy_threshold, sell_threshold = calculate_thresholds()
    if buy_threshold is None or sell_threshold is None:
        print("Chýbajú prahové hodnoty pre rozhodovanie.")
        return

    # Načítame dnešné ceny
    today_prices, _ = get_prices(day_offset=0)

    # Pripojenie k databáze
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    
    # Vytvorenie tabuľky decisions, ak ešte neexistuje
    cursor.execute('''CREATE TABLE IF NOT EXISTS decisions (
                         hour INTEGER PRIMARY KEY,
                         price REAL,
                         decision TEXT
                     )''')
    cursor.execute("DELETE FROM decisions")  # Vymaže staré záznamy

    # Pre každú hodinu určí rozhodnutie a uloží do tabuľky
    for hour, price in today_prices:
        if price <= buy_threshold:
            decision = 'buy'
        elif price >= sell_threshold:
            decision = 'sell'
        else:
            decision = 'hold'
        cursor.execute("INSERT INTO decisions (hour, price, decision) VALUES (?, ?, ?)", (hour, price, decision))
        print(f"Hodina {hour}: Cena {price}, Rozhodnutie: {decision}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    automated_decision()
