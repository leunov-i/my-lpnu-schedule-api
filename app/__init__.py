from flask import Flask
from app.routes import schedule_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(schedule_blueprint)
    return app