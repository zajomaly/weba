import sqlite3
import pandas as pd
from datetime import datetime

def load_historical_data():
    # Pripoj sa k databáze a načítaj historické údaje
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    query = "SELECT date, hour, price FROM prices"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Premeň stĺpec 'date' na typ datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Pridaj nové stĺpce pre deň v týždni a mesiac
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    return df

def analyze_data(df):
    # Vypočítaj priemernú cenu pre každú hodinu
    hourly_avg = df.groupby('hour')['price'].mean()
    
    # Vypočítaj priemernú cenu pre každý deň v týždni
    daily_avg = df.groupby('day_of_week')['price'].mean()
    
    # Vypočítaj priemernú cenu pre každý mesiac
    monthly_avg = df.groupby('month')['price'].mean()
    
    # Vypíš výsledky analýzy
    print("Priemerná cena podľa hodiny:")
    print(hourly_avg)
    print("\nPriemerná cena podľa dňa v týždni:")
    print(daily_avg)
    print("\nPriemerná cena podľa mesiaca:")
    print(monthly_avg)

if __name__ == "__main__":
    data = load_historical_data()
    analyze_data(data)
