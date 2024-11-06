import sqlite3

# Vytvorenie pripojenia k databáze
def create_connection():
    connection = sqlite3.connect('/www/arbitrage/arbitrage.db')
    return connection

# Inicializácia tabuliek v databáze
def initialize_database():
    connection = create_connection()
    cursor = connection.cursor()

    # Tabuľka na ukladanie cien elektriny
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            hour INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Tabuľka na ukladanie nastavení batérie
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS battery_settings (
            id INTEGER PRIMARY KEY,
            capacity REAL,
            power REAL
        )
    ''')

    connection.commit()
    connection.close()

# Spustenie inicializácie
if __name__ == '__main__':
    initialize_database()
