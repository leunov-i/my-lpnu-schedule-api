from flask import Blueprint, jsonify
from .parser import get_schedule_data

api = Blueprint("api", __name__)

@api.route("/api/schedule/<group_name>")
def schedule(group_name):
    try:
        data = get_schedule_data(group_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500