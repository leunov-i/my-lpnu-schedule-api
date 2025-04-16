from flask import Blueprint, jsonify
from .parser import get_schedule_data
from urllib.parse import quote

api = Blueprint("api", __name__)

@api.route("/api/schedule/<group_name>")
def schedule(group_name):
    try:
        group_encoded = quote(group_name)
        data = get_schedule_data(group_encoded)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500