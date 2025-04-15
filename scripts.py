import requests
import aiosqlite
import logging
import time
from datetime import datetime, timedelta
import json
import asyncio
from config import AUTH_KEY, API_URL, DATABASE_NAME, data_json



# Функция для преобразования строковой даты из ответа сайта emall.by
def convert_str_to_date(date_str):
    try:
        # Преобразуем строку даты в объект datetime с указанным форматом
        date_object = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # Приводим объект datetime к timestamp (количество секунд с 1 января 1970 года)
        return int(date_object.timestamp())
    except ValueError as e:  # Обрабатываем возможную ошибку преобразования строки
        # Выводим сообщение об ошибке, если строка не соответствует ожидаемому формату
        print(f"Ошибка преобразования строки даты: {e}")
        return None  # Возвращаем None в случае ошибки









# Инициализация базы данных
async def init_db():
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Создание таблицы users, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS users ("
                             "id INTEGER PRIMARY KEY, "
                             "user_id INTEGER UNIQUE, "
                             "first_name TEXT, "
                             "last_name TEXT, "
                             "username TEXT, "
                             "user_added INTEGER NOT NULL, "
                             "user_blocked INTEGER NOT NULL, "
                             "subscription_status TEXT, "
                             "time_of_add INTEGER)"
                             "")
            # Создание таблицы orders, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS orders ("
                             "id INTEGER PRIMARY KEY,"
                             "number_of_order INTEGER UNIQUE NOT NULL,"
                             "time_start INTEGER,"
                             "time_end INTEGER,"
                             "send_status INTEGER NOT NULL,"
                             "resend_status INTEGER NOT NULL)"
                             "")

            # Создание таблицы positions, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS positions ("
                             "id INTEGER PRIMARY KEY,"
                             "number_of_order INTEGER NOT NULL,"
                             "date_refresh INTEGER)"
                             "")
            await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")



# Добавление пользователя в базу данных
async def add_user_db(user_id, first_name, last_name, username):
    time_of_add = int(time.time())
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Проверка, существует ли пользователь в базе данных
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result is not None:
                    # Если пользователь существует, можно обновить его данные
                    await db.execute("UPDATE users SET first_name = ?, last_name = ?, username = ?, user_added = ? WHERE user_id = ? ", (first_name, last_name, username, 1, user_id))
                    logging.info(f"Пользователь с ID {user_id} обновлен в базе данных.")
                else:
                    # Если не существует, добавляем нового пользователя
                    await db.execute("INSERT INTO users (user_id, first_name, last_name, username, user_added, user_blocked, time_of_add, subscription_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, first_name, last_name, username, 1, 0, time_of_add,'none'))
                    logging.info(f"Пользователь с ID {user_id} добавлен в базу данных.")
                await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при добавлении пользователя в базу данных: {e}")
    except Exception as e:
        logging.error(f"Произошла неожиданная ошибка: {e}")








def get_order():
    url = API_URL + '/open/api/v1/new/orders/products'
    params = {
        'page': '1',
        'perPage': '15',
    }
    headers = {
        'Authorization': 'Bearer ' + AUTH_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers, params=params)  # Используйте requests.get для простоты
        response.raise_for_status()  # Проверка для HTTP ошибок (например, 404, 500 и т.д.)
        x = response.json()  # Получаем JSON ответ от сервера
        return x
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Вывод ошибки для отладки
    except Exception as err:
        print(f"An error occurred: {err}")  # Общая обработка исключений



async def add_order_to_db():
    try:
        data = json.loads(data_json)
        async with aiosqlite.connect(DATABASE_NAME) as db:

            # Извлекаем основные данные
            for entry in data['data']:
                number_of_order = entry['id']
                time_start = convert_str_to_date(entry['time_start'])
                time_end = convert_str_to_date(entry['time_end'])
                send_status=0
                resend_status=0
                async with db.execute("SELECT * FROM orders WHERE number_of_order = ?;", (number_of_order,)) as cursor:
                    result = await cursor.fetchall()
                    if not result:  # Проверяем, пуст ли список
                        await db.execute(
                            F"INSERT INTO orders (number_of_order, time_start, time_end, send_status, resend_status) VALUES (?,?,?,?,?);",
                            (number_of_order, time_start, time_end, send_status, resend_status))

            await db.commit()  # Не забудьте зафиксировать изменения
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")








