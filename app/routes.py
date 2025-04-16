from flask import Blueprint, jsonify
from app.parser import get_schedule_data

schedule_blueprint = Blueprint("schedule", __name__)

@schedule_blueprint.route("/<group>", methods=["GET"])
def get_schedule(group):
    try:
        data = get_schedule_data(group)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500