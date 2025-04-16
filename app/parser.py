import requests
from bs4 import BeautifulSoup # Використовуємо BeautifulSoup4
import re # Може знадобитись для регулярних виразів

# Словник часу пар (перевірити!)
LESSON_TIMES = {
    1: ("08:30", "10:00"), 2: ("10:15", "11:45"), 3: ("12:00", "13:30"),
    4: ("13:45", "15:15"), 5: ("15:30", "17:00"), 6: ("17:15", "18:45"),
    7: ("19:00", "20:30"), 8: ("20:45", "22:15")
}

# Мапінг назв днів (можна розширити)
WEEKDAY_MAP = {
    "пн": 1, "пон": 1, "понеділок": 1,
    "вт": 2, "вів": 2, "вівторок": 2,
    "ср": 3, "сер": 3, "середа": 3,
    "чт": 4, "чет": 4, "четвер": 4,
    "пт": 5, "п’я": 5, "п'ятниця": 5, # Додав апостроф
    "сб": 6, "суб": 6, "субота": 6,
    "нд": 7, "нед": 7, "неділя": 7,
}

def parse_lesson_details(details_str):
    """Розбирає рядок типу 'Викладач П.І., Ауд. 101, Лекція'"""
    parts = [p.strip() for p in details_str.split(',')]
    lecturer = parts[0] if len(parts) > 0 and parts[0] else None
    lesson_type = None
    location = None
    possible_types = ["лекція", "практична", "лабораторна", "консультація"] # В нижньому регістрі

    # Спробуємо знайти тип заняття в кінці
    if len(parts) > 1 and parts[-1].lower() in possible_types:
        lesson_type = parts[-1]
        location_parts = parts[1:-1] # Все між викладачем і типом - це локація
        location = ", ".join(location_parts) if location_parts else None
    elif len(parts) > 1: # Якщо типу немає, все після викладача - локація
        location = ", ".join(parts[1:])

    return (lecturer or None, location or None, lesson_type or None) # Повертаємо None якщо порожньо

def parse_week_type(id_str):
    """Визначає тип тижня з ID (chys, znam, full)"""
    if "_chys" in id_str: return "numerator"
    if "_znam" in id_str: return "denominator"
    return "full"

def get_schedule_data(group_name_encoded):
    """Завантажує та парсить розклад"""
    base_url = "https://student.lpnu.ua/students_schedule"
    params = {
        "studygroup_abbrname": group_name_encoded,
        "semestr": "2",
        "semestrduration": "1"
    }
    headers = { # Додамо User-Agent браузера про всяк випадок
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Requesting URL: {base_url} with params: {params}")
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status() # Кине помилку для статусів 4xx/5xx

        # Спробуємо визначити кодування, якщо Requests не впорався
        response.encoding = response.apparent_encoding # BeautifulSoup краще працює, якщо кодування встановлено
        html_content = response.text
        print(f"HTML content downloaded ({len(html_content)} chars)")

        soup = BeautifulSoup(html_content, 'html.parser')

        # Шукаємо контейнер (спробуємо обидва варіанти)
        content_div = soup.find('div', class_='view-content')
        if not content_div:
            content_div = soup.find('div', class_='region-content') # Запасний варіант

        if not content_div:
            # Перевіряємо, чи повернулася форма пошуку (ознака, що група не знайдена)
            if soup.find('form', id='views-exposed-form-students-schedule-new-students-schedule'):
                 print(f"Schedule not found for group (form present). Encoded name: {group_name_encoded}")
                 return [] # Повертаємо порожній список
            else:
                 print("Error: Could not find schedule container ('view-content' or 'region-content')")
                 raise ValueError("Schedule container not found") # Кидаємо помилку парсингу

        schedule_by_day = {}
        current_day_iso = None
        current_lesson_num = None

        # Ітеруємо по елементах всередині знайденого контейнера
        # Важливо: селектори можуть потребувати адаптації!
        for element in content_div.find_all(['span', 'h3', 'div'], recursive=False): # Шукаємо лише прямих нащадків? Або всіх? Спробуємо recursive=False
            if element.name == 'span' and 'view-grouping-header' in element.get('class', []):
                day_name = element.get_text(strip=True).lower()
                current_day_iso = WEEKDAY_MAP.get(day_name)
                current_lesson_num = None
                if current_day_iso and current_day_iso not in schedule_by_day:
                    schedule_by_day[current_day_iso] = []
                print(f"Found day: {day_name} -> ISO: {current_day_iso}")
            elif element.name == 'h3':
                try:
                    current_lesson_num = int(element.get_text(strip=True))
                    print(f"Found lesson number: {current_lesson_num}")
                except (ValueError, TypeError):
                    current_lesson_num = None
                    print(f"Warning: Could not parse lesson number from H3: {element.get_text(strip=True)}")
            elif element.name == 'div' and 'stud_schedule' in element.get('class', []) and current_day_iso and current_lesson_num:
                print(f"Processing lesson block for day {current_day_iso}, number {current_lesson_num}")
                lesson_containers = element.find_all('div', id=re.compile(r'^(sub_|group_)')) # Знаходимо div з id sub_... або group_...
                for container in lesson_containers:
                    container_id = container.get('id', '')
                    week_type = parse_week_type(container_id)
                    content_div_inner = container.find('div', class_='group_content')
                    if not content_div_inner: continue

                    nodes = content_div_inner.contents # Отримуємо список всіх дочірніх вузлів
                    subject = nodes[0].strip() if nodes and isinstance(nodes[0], str) else "N/A"
                    details_line = ""
                    if len(nodes) > 2 and nodes[1].name == 'br' and isinstance(nodes[2], str):
                        details_line = nodes[2].strip()

                    link_tag = content_div_inner.find('span', class_='schedule_url_link')
                    online_url = link_tag.find('a')['href'] if link_tag and link_tag.find('a') else None

                    lecturer, location, lesson_type = parse_lesson_details(details_line)
                    time = LESSON_TIMES.get(current_lesson_num, ("??:??", "??:??"))

                    lesson_data = {
                        "subject": subject,
                        "timeStart": time[0],
                        "timeEnd": time[1],
                        "lessonNumber": current_lesson_num,
                        "lecturer": lecturer,
                        "location": location,
                        "lessonType": lesson_type,
                        "onlineLessonUrl": online_url,
                        "weekType": week_type,
                        # "groupName": group_name # Додамо в routes.py
                    }
                    if current_day_iso in schedule_by_day:
                       schedule_by_day[current_day_iso].append(lesson_data)
                    print(f"  Parsed lesson: {subject}")

        # Формуємо фінальний JSON-сумісний список
        result_list = [{"dayOfWeek": day, "lessons": lessons} for day, lessons in schedule_by_day.items()]
        result_list.sort(key=lambda x: x['dayOfWeek']) # Сортуємо
        print(f"Parsing finished. Found data for {len(result_list)} days.")
        return result_list

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        raise ConnectionError(f"Network error: {e}")
    except ValueError as e: # Ловимо нашу помилку парсингу
         print(f"Parsing Error: {e}")
         raise e
    except Exception as e:
        print(f"Unexpected Parsing Error: {e}")
        raise ValueError(f"Unexpected parsing error: {e}")