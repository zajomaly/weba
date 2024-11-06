from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    battery_threshold = db.Column(db.Float)
    solar_installed = db.Column(db.Boolean)

    def __init__(self, battery_threshold, solar_installed):
        self.battery_threshold = battery_threshold
        self.solar_installed = solar_installed
