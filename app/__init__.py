from flask import Flask
import os

# Можна додати конфігурацію, якщо потрібно
# from config import Config

app = Flask(__name__)
# app.config.from_object(Config) # Якщо є конфігурація

# Реєструємо наші маршрути (API endpoints)
from app import routes

print("Flask app created") # Для відладки