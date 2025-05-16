from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from scripts import get_status_user_db, set_status_user_db
from config import LISTOFADMINS

start_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="По запросу", callback_data='По запросу'), InlineKeyboardButton(text="⚙️ Настройки", callback_data='Настройки')]
    ])

start_keyboard_reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💸 Курсы популярных валют"), KeyboardButton(text="📝 Все курсы")],
    [KeyboardButton(text="⚙️ Меню")]
    ], resize_keyboard=True)



start_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Зарегистрироваться", callback_data='pasword')]
])



menu_keyboard_inline_11 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пригласить пользователя", callback_data='menu11')],
    [InlineKeyboardButton(text="Посмотреть/удалить", callback_data='menu12')],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='menu13')]

])

menu_keyboard_inline_111 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сгенерировать еще", callback_data='menu111')],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='menu112')]

])

menu_keyboard_inline_121 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data='menu121')]

])





menu_keyboard_inline_21 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Уведомления с фото", callback_data='menu21')],
    [InlineKeyboardButton(text="Уведомления без фото", callback_data='menu22')],
    [InlineKeyboardButton(text="Не присылать уведомления", callback_data='menu23')],
[InlineKeyboardButton(text="Присылать в любое время", callback_data='menu24')],
[InlineKeyboardButton(text="Присылать с Пн по Пт с 09 по 18", callback_data='menu25')],
    [InlineKeyboardButton(text="🔙 Назад", callback_data='menu26')]

])



menu_keyboard_inline_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data='menu31')]

])



async def menu_keyboard_inline_1(tgid):
    button_texts = {
        'users': 'Управление пользователями',
        'uved': 'Управление уведомлениями',
        'help': 'Помощь',
        'developer':'Написать разработчику',
        'exit': '🔙 Выйти из Меню'
    }

    # Базовый набор кнопок
    buttons = [
        [InlineKeyboardButton(text=button_texts['uved'], callback_data='menu2')],
        [InlineKeyboardButton(text=button_texts['help'], callback_data='menu3')],
        [InlineKeyboardButton(text=button_texts['developer'], callback_data='developer')],
        [InlineKeyboardButton(text=button_texts['exit'], callback_data='menu4')]
    ]

    # Если пользователь является администратором, добавляем кнопку управления пользователями
    if tgid in LISTOFADMINS:
        buttons.insert(0, [InlineKeyboardButton(text=button_texts['users'], callback_data='menu1')])

    dynamic_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return dynamic_keyboard






menu_keyboard_reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💸 Курсы популярных валют"), KeyboardButton(text="📝 Все курсы")],
    [KeyboardButton(text="⚙️ Меню")]
    ], resize_keyboard=True)






async def create_dynamic_keyboard_select(tgid, type_of_notification, notification_frequency):
    # Получаем статус подписки пользователя из базы данных
    status = await get_status_user_db(tgid)
    if type_of_notification == 'full':
        button_text1 = '🟢 Уведомления с фото'
        button_text2 = '🔘 Уведомления без фото'


    elif type_of_notification == 'short':
        button_text1 = '🔘 Уведомления с фото'
        button_text2 = '🟢 Уведомления без фото'


    elif type_of_notification == 'none':
        if status[0] == 'full':
            button_text1 = '🟢 Уведомления с фото'
            button_text2 = '🔘 Уведомления без фото'
        elif status[0] == 'short':
            button_text1 = '🔘 Уведомления с фото'
            button_text2 = '🟢 Уведомления без фото'



    if notification_frequency == 'never':
        button_text3 = '🟢 Не присылать уведомления'
        button_text4 = '🔘 Присылать в любое время'
        button_text5 = '🔘 Присылать Пн-Пт с 09 по 18'

    elif notification_frequency == 'alltime':
        button_text3 = '🔘 Не присылать уведомления'
        button_text4 = '🟢 Присылать в любое время'
        button_text5 = '🔘 Присылать Пн-Пт с 09 по 18'

    elif notification_frequency == 'worktime':
        button_text3 = '🔘 Не присылать уведомления'
        button_text4 = '🔘 Присылать в любое время'
        button_text5 = '🟢 Присылать Пн-Пт с 09 по 18'

    elif notification_frequency == 'none':
        if status[1] == 'never':
            button_text3 = '🟢 Не присылать уведомления'
            button_text4 = '🔘 Присылать в любое время'
            button_text5 = '🔘 Присылать Пн-Пт с 09 по 18'

        elif status[1] == 'alltime':
            button_text3 = '🔘 Не присылать уведомления'
            button_text4 = '🟢 Присылать в любое время'
            button_text5 = '🔘 Присылать Пн-Пт с 09 по 18'

        elif status[1] == 'worktime':
            button_text3 = '🔘 Не присылать уведомления'
            button_text4 = '🔘 Присылать в любое время'
            button_text5 = '🟢 Присылать Пн-Пт с 09 по 18'

    button_text6 = '🔙 Назад'


    await set_status_user_db(tgid, type_of_notification, notification_frequency)

    # Создание динамической клавиатуры с учетом статуса подписки
    dynamic_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text1, callback_data='full')],
        [InlineKeyboardButton(text=button_text2, callback_data='short')],
        [InlineKeyboardButton(text=button_text3, callback_data='never')],
        [InlineKeyboardButton(text=button_text4, callback_data='alltime')],
        [InlineKeyboardButton(text=button_text5, callback_data='worktime')],
        [InlineKeyboardButton(text=button_text6 , callback_data='menu26')]
    ])

    return dynamic_keyboard
