from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta
import statistics

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Zmeňte na bezpečný kľúč

def get_prices(day_offset=0):
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    target_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
    cursor.execute("SELECT hour, price FROM prices WHERE date = ?", (target_date,))
    prices = cursor.fetchall()
    conn.close()
    return prices or [], target_date

def get_predicted_prices(day_offset):
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    future_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
    cursor.execute("SELECT hour, ROUND(price, 2) FROM predicted_prices WHERE date = ?", (future_date,))
    predicted_prices = cursor.fetchall()
    conn.close()

    unique_predicted_prices = {}
    for hour, price in predicted_prices:
        if hour not in unique_predicted_prices:
            unique_predicted_prices[hour] = price

    sorted_unique_predicted_prices = sorted(unique_predicted_prices.items())
    return sorted_unique_predicted_prices, future_date

def get_historical_prices():
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    past_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("SELECT date, hour, price FROM prices WHERE date >= ?", (past_week,))
    historical_prices = cursor.fetchall()
    conn.close()
    return historical_prices or []

def calculate_thresholds():
    historical_prices = [price for _, _, price in get_historical_prices()]
    if not historical_prices:
        return None, None

    avg_price = statistics.mean(historical_prices)
    std_dev = statistics.stdev(historical_prices)

    # Dynamické prahy: Nákup pod priemerom mínus odchýlka, predaj nad priemerom plus odchýlka
    buy_threshold = avg_price - std_dev
    sell_threshold = avg_price + std_dev

    return buy_threshold, sell_threshold

def get_decisions_from_db():
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    cursor.execute("SELECT hour, price, decision FROM decisions ORDER BY hour")
    decisions = cursor.fetchall()
    conn.close()
    return decisions

@app.route('/')
def index():
    today_prices, today_date = get_prices(day_offset=0)
    tomorrow_prices, tomorrow_date = get_prices(day_offset=1)
    predicted_prices_day_after, future_date_day_after = get_predicted_prices(day_offset=2)
    historical_prices = get_historical_prices()
    decisions = get_decisions_from_db()  # Načítanie rozhodnutí z databázy

    historical_labels = [f"{date} {hour}:00" for date, hour, _ in historical_prices]
    historical_data = [price for _, _, price in historical_prices]

    return render_template('index.html',
                           today_prices=today_prices,
                           today_date=today_date,
                           tomorrow_prices=tomorrow_prices,
                           tomorrow_date=tomorrow_date,
                           predicted_prices_day_after=predicted_prices_day_after,
                           future_date_day_after=future_date_day_after,
                           historical_labels=historical_labels,
                           historical_data=historical_data,
                           decisions=decisions)  # Odovzdanie rozhodnutí do šablóny
# Trasa pre nastavenia batérie
@app.route('/battery-settings')
def battery_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('battery_settings.html')
# Trasa pre nastavenia fotovoltaiky
@app.route('/solar-settings')
def solar_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('solar_settings.html')

# Trasa pre nastavenia cien
@app.route('/price-settings')
def price_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('price_settings.html')

# Trasa pre nastavenia elektromera
@app.route('/meter-settings')
def meter_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('meter_settings.html')
# Trasa na uloženie nastavení batérie
@app.route('/save-battery-settings', methods=['POST'])
def save_battery_settings():
    battery_capacity = request.form['capacity']
    battery_power = request.form['power']
    threshold_type = request.form['threshold_type']

    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()

    if threshold_type == 'fixed':
        charge_threshold = request.form['charge_threshold']
        discharge_threshold = request.form['discharge_threshold']
        cursor.execute(
            "INSERT INTO battery_settings (capacity, power, charge_threshold, discharge_threshold) VALUES (?, ?, ?, ?)",
            (battery_capacity, battery_power, charge_threshold, discharge_threshold)
        )
    else:
        charge_threshold, discharge_threshold = calculate_thresholds()
        if charge_threshold is not None and discharge_threshold is not None:
            cursor.execute(
                "INSERT INTO battery_settings (capacity, power, charge_threshold, discharge_threshold) VALUES (?, ?, ?, ?)",
                (battery_capacity, battery_power, charge_threshold, discharge_threshold)
            )

    conn.commit()
    conn.close()
    flash('Nastavenia batérie boli úspešne uložené.')
    return redirect(url_for('settings'))  # Upravte na správnu trasu

# Trasa na uloženie nastavení fotovoltaiky
@app.route('/save-solar-settings', methods=['POST'])
def save_solar_settings():
    installed = request.form.get('installed') == 'on'  # Kontrola, či je fotovoltaika nainštalovaná
    inverter_capacity = request.form['inverter_capacity'] if installed else None  # Uložíme len ak je nainštalovaná

    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO solar_settings (installed, inverter_capacity) VALUES (?, ?)",
        (installed, inverter_capacity)
    )
    conn.commit()
    conn.close()

    flash('Nastavenia fotovoltaiky boli úspešne uložené.')
    return redirect(url_for('settings'))  # Upravte na správnu trasu

# Trasa na uloženie nastavení cien
@app.route('/save-price-settings', methods=['POST'])
def save_price_settings():
    distribution_price = request.form['distribution_price']
    purchase_price = request.form['purchase_price']
    monthly_fee = request.form['monthly_fee']

    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO price_settings (distribution_price, purchase_price, monthly_fee) VALUES (?, ?, ?)",
        (distribution_price, purchase_price, monthly_fee)
    )
    conn.commit()
    conn.close()

    flash('Nastavenia cien boli úspešne uložené.')
    return redirect(url_for('settings'))  # Upravte na správnu trasu

# Trasa na uloženie nastavení elektromera
@app.route('/save-meter-settings', methods=['POST'])
def save_meter_settings():
    meter_type = request.form['meter_type']
    meter_capacity = request.form['meter_capacity']

    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meter_settings (type, capacity) VALUES (?, ?)",
        (meter_type, meter_capacity)
    )
    conn.commit()
    conn.close()

    flash('Nastavenia elektromera boli úspešne uložené.')
    return redirect(url_for('settings'))  # Upravte na správnu trasu

# Trasa pre prihlasovaciu stránku
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_login(username, password):
            session['logged_in'] = True
            return redirect(url_for('settings'))
        else:
            flash('Nesprávne meno alebo heslo')
    return render_template('login.html')

# Funkcia na kontrolu prihlasovacích údajov
def check_login(username, password):
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Trasa pre hlavnú stránku „Nastavenia“
@app.route('/settings')
def settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('settings.html')

# Trasa pre odhlásenie
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Boli ste odhlásený')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
