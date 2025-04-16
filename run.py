from app import app

if __name__ == '__main__':
    # Запускаємо на порту 5000 для локальної розробки
    app.run(host='0.0.0.0', port=5001, debug=True) # Використовуємо порт 5001