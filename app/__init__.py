from flask import Flask
from app.routes import api  # або що там у тебе

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)
    return app