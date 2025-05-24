import requests
import aiosqlite
import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile
import time
from datetime import datetime, timedelta, timezone
import json
import asyncio
from config import AUTH_KEY, API_URL, DATABASE_NAME

import string
import random




# Функция для преобразования строковой даты из ответа сайта emall.by
def convert_str_to_date(date_str):
    try:
        # Преобразуем строку даты в объект datetime с указанным форматом
        date_object = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # Приводим объект datetime к timestamp (количество секунд с 1 января 1970 года)
        return int(date_object.timestamp())
    except ValueError as e:  # Обрабатываем возможную ошибку преобразования строки
        # Выводим сообщение об ошибке, если строка не соответствует ожидаемому формату
        logging.error(f"Ошибка преобразования строки даты: {e}")
        return None  # Возвращаем None в случае ошибки


# Функция для преобразования временной метки в строковую дату
def convert_date_to_str(date_sec,hours):
    try:
        # Преобразуем временную метку (timestamp) в объект time.struct_time в формате UTC
        date_object = time.gmtime(date_sec+(hours*60*60))
        # Форматируем объект time.struct_time в строку в формате "YYYY-MM-DD"
        naive_datetime = time.strftime("%H:%M %d.%m.%Y", date_object)



        return naive_datetime  # Возвращаем отформатированную строку даты
    except Exception as e:  # Обрабатываем любые исключения, которые могут произойти
        # Выводим сообщение об ошибке, если произошла ошибка во время преобразования
        logging.error(f"Ошибка преобразования даты: {e}")
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
                             "type_of_notification TEXT, "
                             "notification_frequency TEXT,"
                             "time_of_add INTEGER)"
                             "")
            # Создание таблицы orders, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS orders ("
                             "id INTEGER PRIMARY KEY,"
                             "number_of_order INTEGER UNIQUE NOT NULL,"
                             "order_cost INTEGER,"
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
                             "positions_number INTEGER,"
                             "positions_name TEXT,"
                             "quantity INTEGER,"
                             "price INTEGER,"
                             "total_price INTEGER,"
                             "image_url TEXT,"
                             "date_refresh INTEGER)"
                             "")
            # Создание таблицы passwords, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS passwords ("
                             "id INTEGER PRIMARY KEY,"
                             "time_of_add INTEGER,"
                             "password TEXT,"
                             "status INTEGER)"
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
                    await db.execute("INSERT INTO users (user_id, first_name, last_name, username, user_added, user_blocked, time_of_add, type_of_notification, notification_frequency ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)", (user_id, first_name, last_name, username, 1, 0, time_of_add,'full','never'))
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
        logging.error(f"HTTP error occurred: {http_err}")  # Вывод ошибки для отладки
    except Exception as err:
        logging.error(f"An error occurred: {err}")  # Общая обработка исключений



async def add_order_to_db():
    try:
        data = get_order()
        if data != None:

            async with aiosqlite.connect(DATABASE_NAME) as db:

                # Извлекаем основные данные
                for entry in data['data']:
                    number_of_order = entry['id']
                    time_start = convert_str_to_date(entry['time_start'])
                    time_end = convert_str_to_date(entry['time_end'])
                    send_status=0
                    resend_status=0
                    for box in entry['boxes']:
                        order_cost = box['item_price']

                        async with db.execute("SELECT * FROM orders WHERE number_of_order = ?;", (number_of_order,)) as cursor:
                            result = await cursor.fetchall()
                            if not result:  # Проверяем, пуст ли список
                                await db.execute(
                                    F"INSERT INTO orders (number_of_order, order_cost, time_start, time_end, send_status, resend_status) VALUES (?,?,?,?,?,?);",
                                    (number_of_order, order_cost, time_start, time_end, send_status, resend_status))
                                for box in entry['boxes']:
                                    position = 0
                                    for item in box['items']:
                                        position += 1
                                        offer = item['offer']
                                        if 'images' in offer:
                                            image_url = offer['images'][0]
                                        positions_number = position
                                        positions_name = offer['name']
                                        quantity = item['quantity']
                                        price = item['price']
                                        total_price = item['total_price']



                                        await db.execute(
                                            F"INSERT INTO positions (number_of_order, positions_number, positions_name, quantity, price, total_price, image_url) VALUES (?,?,?,?,?,?,?);",
                                            (number_of_order, positions_number, positions_name, quantity, price, total_price, image_url))





                await db.commit()  # Не забудьте зафиксировать изменения
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")


async def get_number_order_from_db(send_status, resend_status):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT * FROM orders WHERE send_status = ? AND resend_status = ?",
                                  (send_status, resend_status,)) as cursor:
                result = await cursor.fetchall()
                list_of_orders = [number_of_order[1] for number_of_order in
                                  result]  # Предполагаем, что номер заказа находится на втором месте.
                return list_of_orders  # Возвращаем список заказов.

    except aiosqlite.Error as e:
        logging.error(f"Возникла ошибка: {e}")
        return []  # Возвращаем пустой список в случае ошибки.




async def get_all_info_order_from_db(number_of_order):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT * FROM orders WHERE number_of_order = ?",
                                  (number_of_order,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    logging.info(f"Заказ с номером {number_of_order} не найден.")
                return result  # Возвращаем результат или None, если не найдено.

    except aiosqlite.Error as e:
        logging.error(f"Возникла ошибка при доступе к базе данных: {e}")
        return None  # Возвращаем None для указания на ошибку.





async def set_status_number_order_from_db(number_of_order, send_status, resend_status):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Обновление статуса заказа
            await db.execute(
                "UPDATE orders SET send_status=?, resend_status=? WHERE number_of_order = ?",
                (send_status, resend_status, number_of_order)
            )
            await db.commit()
            logging.info(f"Статус заказа № {number_of_order} успешно обновлен: sent_status={send_status}, resend_status={resend_status}")

    except aiosqlite.Error as e:
        logging.error(f"Возникла ошибка при обновлении статуса заказа: {e}")






async def get_positions_from_db(number_of_order):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT * FROM positions WHERE number_of_order = ?", (number_of_order,)) as cursor:
                result = await cursor.fetchall()

                if not result:
                    logging.info(f"Заказ с номером {number_of_order} не найден.")
                    return None  # Или можно вернуть [] в зависимости от вашего подхода.

                return result  # Возвращаем список заказов.

    except aiosqlite.Error as e:
        logging.error(f"Возникла ошибка базы данных: {e}")
        return None  # Позволяет вызывать эту функцию, зная, что обработка ошибки выполнена.









async def rassilka_full(bot: Bot):
    list_of_orders = await get_number_order_from_db(0, 0)

    if list_of_orders:
        full_worktime = await get_list_user_with_status_db('full','worktime')
        full_alltime = await get_list_user_with_status_db('full', 'alltime')
        short_worktime = await get_list_user_with_status_db('short', 'worktime')
        short_alltime = await get_list_user_with_status_db('short', 'alltime')

        for number_order in list_of_orders:
            info_order = await get_all_info_order_from_db(number_order)
            await set_status_number_order_from_db(number_order, 1, 0)
            text_bot = (f"<b>Заказ №: {number_order}</b>\nСтоимость заказа: <b>{info_order[2]} BYN</b>\n"
                        f"Передать заказ в доставку до: <b>{convert_date_to_str(info_order[3],3)}</b>\n"
                        f"Подробную информацию можно получить перейдя на сайт emall - https://b2b.emall.by/orders "
                        )
            message_text_short = ''

            if can_send_message():
                full_all_list = full_worktime + full_alltime
            else:

                full_all_list = full_alltime

            if can_send_message():
                short_all_list = short_worktime + short_alltime
            else:

                short_all_list = short_alltime







            for user in full_all_list:
                try:
                    photo = FSInputFile("image/red.png")
                    await bot.send_photo(chat_id=user, photo=photo, caption=text_bot, parse_mode='HTML')

                except Exception as e:
                    logging.error(f"Ошибка при отправке сообщения пользователю {user}: {e}")


            list_of_positions = await get_positions_from_db(number_order)
            for position in list_of_positions:

                message_text_full = (f"<b>Позиция {position[2]}:</b>\n"
                                f"<i>(в составе заказа {number_order})</i>\n\n"
                                f"{position[3]}\n\n"
                                f"Количество: <b>{position[4]} шт.</b>\n"
                                f"<i>Цена: {position[5]}</i>\n"
                                f"<i>Общая сумма: {position[6]}</i>"
                                )

                message_text_short = message_text_short + (f"<b>Позиция {position[2]}:</b>\n"
                                               f"{position[3]}\n"
                                               f"Количество: <b>{position[4]} шт.</b>\n"
                                               f"<i>Цена: {position[5]}</i>\n"
                                               f"<i>Общая сумма: {position[6]}</i>\n\n"
                                               )

                photo = URLInputFile(position[7])  # Убедитесь, что это ссылка на изображение или путь к файлу

                    # Отправка изображения (раскомментируйте, если необходимо)
                for user in full_all_list:
                    try:
                        await bot.send_photo(chat_id=user, photo=photo, caption=message_text_full, parse_mode='HTML')

                    except Exception as e:
                        logging.error(f"Ошибка при отправке сообщения пользователю {user}: {e}")
            message_text_short = text_bot+'\n\n' + message_text_short
            for user in short_all_list:
                try:
                    await bot.send_message(chat_id=user, text=message_text_short, parse_mode='HTML')

                except Exception as e:
                    logging.error(f"Ошибка при отправке сообщения пользователю {user}: {e}")












def generate_password(length):
    # Используем только буквы и цифры
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


async def add_password_db():
    password = generate_password(20)
    time_of_add = int(time.time())
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute("INSERT INTO passwords (time_of_add, password, status) VALUES (?,?,?);", (time_of_add, password, 0))
            await db.commit()
        return password
    except Exception as e:
        logging.error(f"Ошибка в функции add_password_db: {e}")


async def get_password_db(password):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT * FROM passwords WHERE password = ?", (password,)) as cursor:
                result = await cursor.fetchone()

                if result is None:
                    return False  # Пароль не найден
                else:

                    return True  # Пароль найден
    except Exception as e:
        logging.error(f"Ошибка в функции get_password_db: {e}")



async def check_del_password_db():
    present_time = int(time.time())
    present_time_10 = present_time - 600
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute("DELETE FROM passwords WHERE time_of_add < ?", (present_time_10,))
            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка в функции check_del_password_db: {e}")


async def del_password_db(password):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute("DELETE FROM passwords WHERE password = ?", (password,))
            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка в функции del_password_db: {e}")



#удаление пользователя
async def del_user_db(user_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка в функции del_user_db: {e}")




#Получение статуса подписки
async def get_status_user_db(user_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT type_of_notification, notification_frequency  FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()

                if result is None:
                    # Если пользователь не найден
                    logging.info(f"Пользователь с ID {user_id} не найден.")
                    return None  # Пользователь не найден


                return result
    except aiosqlite.Error as e:
        # Обработка ошибок базы данных
        logging.error(f"Ошибка доступа к базе данных при получении статуса подписки пользователя {user_id}: {e}")
        return None  # В случае ошибки также можем вернуть None



# Получение списка пользователей
async def get_list_user_db(user_added):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT user_id FROM users WHERE user_added = ?", (user_added,)) as cursor:
                subscribed_users = await cursor.fetchall()  # Здесь должен быть await для получения результата
                user_ids = [user[0] for user in subscribed_users]
                return user_ids
    except aiosqlite.Error as e:
        # Логируем ошибку или обрабатываем её как-то иначе
        logging.error(f"Произошла ошибка при получении списка пользователей: {e}")
        return []  # Возвращаем пустой список в случае ошибки





# Получение списка пользователей
async def get_list_user_with_status_db(type_of_notification, notification_frequency):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT * FROM users WHERE type_of_notification = ? AND notification_frequency = ?", (type_of_notification, notification_frequency,)) as cursor:
                subscribed_users = await cursor.fetchall()  # Здесь должен быть await для получения результата
                user_ids = [user[1] for user in subscribed_users]
                return user_ids
    except aiosqlite.Error as e:
        # Логируем ошибку или обрабатываем её как-то иначе
        logging.error(f"Произошла ошибка при получении списка пользователей: {e}")
        return []  # Возвращаем пустой список в случае ошибки




# Получение списка пользователей
async def get_list_user_for_admins_db(user_added,user_blocked):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            async with db.execute("SELECT * FROM users WHERE user_added = ? AND user_blocked = ?", (user_added,user_blocked,)) as cursor:
                list_user_for_admins = await cursor.fetchall()  # Здесь должен быть await для получения результата

                return list_user_for_admins
    except aiosqlite.Error as e:
        # Логируем ошибку или обрабатываем её как-то иначе
        logging.error(f"Произошла ошибка при получении списка пользователей: {e}")
        return []  # Возвращаем пустой список в случае ошибки





# Запись статуса подписки в базу
async def set_status_user_db(user_id, type_of_notification, notification_frequency):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Формируем SQL запрос и параметры на основе переданных значений
            if type_of_notification != 'none':
                query = "UPDATE users SET type_of_notification=? WHERE user_id=?"
                params = (type_of_notification, user_id)
            elif notification_frequency != 'none':
                query = "UPDATE users SET notification_frequency=? WHERE user_id=?"
                params = (notification_frequency, user_id)
            else:
                logging.warning(f"Пользователь с ID {user_id} попытался установить 'none' для обоих параметров.")
                return  # Выход из функции, если оба параметры 'none'

            async with db.execute(query, params) as cursor:
                await db.commit()
                # Проверка количества обновленных строк
                if cursor.rowcount == 0:
                    logging.warning(f"Пользователь с ID {user_id} не найден для обновления.")

    except aiosqlite.Error as e:
        logging.error(f"Ошибка базы данных при обработке подписки пользователя {user_id}: {e}")
    except Exception as e:
        logging.error(f"Произошла неожиданная ошибка обработки подписки пользователя {user_id}: {e}")




def can_send_message():
    now = datetime.now()
    # Проверяем, что сейчас будний день (0 = понедельник, 6 = воскресенье)
    if now.weekday() < 5:  # Будние дни
        # Проверяем, что время от 9 до 18
        if 9 <= now.hour < 18:
            return True
    return False
