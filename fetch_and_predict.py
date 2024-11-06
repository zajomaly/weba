import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

# Priemerné hodnoty pre hodiny, dni a mesiace
def load_historical_averages():
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    query_hour = "SELECT hour, AVG(price) as avg_price FROM prices GROUP BY hour"
    query_day = "SELECT day_of_week, AVG(price) as avg_price FROM prices GROUP BY day_of_week"
    query_month = "SELECT month, AVG(price) as avg_price FROM prices GROUP BY month"
    
    avg_hour = pd.read_sql_query(query_hour, conn).set_index('hour')['avg_price'].to_dict()
    avg_day = pd.read_sql_query(query_day, conn).set_index('day_of_week')['avg_price'].to_dict()
    avg_month = pd.read_sql_query(query_month, conn).set_index('month')['avg_price'].to_dict()
    
    conn.close()
    return avg_hour, avg_day, avg_month

avg_hour, avg_day, avg_month = load_historical_averages()

# Príprava údajov pre model
def prepare_data():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    url = f"https://isot.okte.sk/api/v1/dam/results?deliveryDayFrom={start_date}&deliveryDayTo={end_date}"
    response = requests.get(url)
    data = response.json()

    prices = []
    for entry in data:
        date = entry['deliveryDay']
        hour = entry['period']
        price = entry['price']
        day_of_week = datetime.strptime(date, '%Y-%m-%d').weekday()
        month = datetime.strptime(date, '%Y-%m-%d').month
        prices.append({
            'date': date,
            'hour': hour,
            'price': price,
            'avg_hour': avg_hour.get(hour, 0),
            'avg_day': avg_day.get(day_of_week, 0),
            'avg_month': avg_month.get(month, 0)
        })
    df = pd.DataFrame(prices)
    return df

df = prepare_data()
df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
df['month'] = pd.to_datetime(df['date']).dt.month
X = df[['hour', 'avg_hour', 'day_of_week', 'avg_day', 'month', 'avg_month']]
y = df['price']

model = LinearRegression()
model.fit(X, y)

# Predikcia na pozajtrajší deň
def predict_prices():
    conn = sqlite3.connect('/www/arbitrage/arbitrage.db')
    cursor = conn.cursor()
    day_after_tomorrow = datetime.now().date() + timedelta(days=2)
    predictions = []
    for hour in range(1, 25):
        avg_hour_value = avg_hour.get(hour, 0)
        avg_day_value = avg_day.get(day_after_tomorrow.weekday(), 0)
        avg_month_value = avg_month.get(day_after_tomorrow.month, 0)

        # Príprava vstupu s pridanými názvami stĺpcov pre predikciu
        input_data = pd.DataFrame(
            [[hour, avg_hour_value, day_after_tomorrow.weekday(), avg_day_value, day_after_tomorrow.month, avg_month_value]],
            columns=['hour', 'avg_hour', 'day_of_week', 'avg_day', 'month', 'avg_month']
        )
        prediction = model.predict(input_data)
        predictions.append((day_after_tomorrow, hour, prediction[0]))
        cursor.execute("INSERT INTO predicted_prices (date, hour, price) VALUES (?, ?, ?)", (day_after_tomorrow, hour, prediction[0]))
    
    conn.commit()
    conn.close()
    return predictions

predictions = predict_prices()
print("Predikované ceny na pozajtra:")
for date, hour, price in predictions:
    print(f"{hour}:00 - {price:.2f} €")
