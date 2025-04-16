from flask import jsonify, abort
from app import app # Імпортуємо app з __init__.py
from app.parser import get_schedule_data # Імпортуємо функцію парсингу
import urllib.parse

@app.route('/api/v1/schedule/group/<string:group_name_raw>', methods=['GET'])
def get_group_schedule(group_name_raw):
    # Декодуємо назву групи з URL, якщо вона закодована
    try:
        group_name = urllib.parse.unquote(group_name_raw)
        print(f"API request for group: {group_name} (raw: {group_name_raw})")
    except Exception as e:
         print(f"Error decoding group name: {e}")
         group_name = group_name_raw # Use raw if decoding fails

    try:
        # Викликаємо парсер, передаючи оригінальну (можливо закодовану) назву, як вона в URL
        schedule_data = get_schedule_data(group_name_raw)

        if not schedule_data:
            # Якщо парсер повернув порожній список (можливо, група не знайдена)
            # Повертаємо 404 або порожній JSON? Повернемо порожній масив.
            print(f"No schedule data found by parser for group: {group_name}")
            return jsonify([])
        else:
            # Додаємо groupName до кожного уроку (якщо потрібно на клієнті)
            for day in schedule_data:
                for lesson in day.get("lessons", []):
                    lesson["groupName"] = group_name # Додаємо розкодовану назву
            return jsonify(schedule_data)
    except ValueError as e:
        # Помилка парсингу або "контейнер не знайдено"
        print(f"Value error processing group {group_name}: {e}")
        abort(500, description=str(e)) # Помилка сервера
    except ConnectionError as e:
         # Помилка мережі при запиті до сайту НУЛП
         print(f"Connection error processing group {group_name}: {e}")
         abort(502, description=str(e)) # Помилка Bad Gateway
    except Exception as e:
        # Інші неочікувані помилки
        print(f"Unexpected error processing group {group_name}: {e}")
        abort(500, description="Internal server error")

# Додаткові маршрути (наприклад, для викладачів) можна додати тут