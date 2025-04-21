from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ULNAME, LISTOFADMINS, BOTNAME
from scripts import add_user_db, add_password_db, get_password_db, del_password_db, get_list_user_db
from keyboards import start_keyboard_inline, menu_keyboard_inline_1, menu_keyboard_inline_11, menu_keyboard_inline_111, menu_keyboard_inline_121, menu_keyboard_inline_21, menu_keyboard_inline_3, create_dynamic_keyboard_select


class Reg(StatesGroup):
    password = State()


router = Router()
@router.message(CommandStart())
async def cmd_start(message: Message):
    list_of_users_from_db = await get_list_user_db(1)
    if message.from_user.id in LISTOFADMINS+list_of_users_from_db:
        #Записываем пользователя в базу
        await add_user_db(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        try:
            # Создаем объект для фотографии
            photo = FSInputFile("image/emall-logo.png")

            # Определяем текст сообщения
            welcome_text = (
                f"👋 <b>Добро пожаловать!</b>\n\n"
                f"Это корпоративный бот {ULNAME}.\n\n"
                f"Бот может уведомлять Вас о новых заказах на маркетплейсе Emall."
            )

            # Отправляем фотографию с текстом
            await message.answer_photo(photo=photo, caption=welcome_text, parse_mode=ParseMode.HTML)
            await message.answer(f"Воспользуйтесь клавиатурой", reply_markup=await menu_keyboard_inline_1(message.from_user.id), parse_mode=ParseMode.HTML)

        except FileNotFoundError:
            await message.answer("Извините, изображение не найдено. Пожалуйста, обратитесь к администратору.")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")

    else:
            await message.answer("Обратитесь к администратору или зарегистрируйтесь:", reply_markup=start_keyboard_inline)





@router.message(Reg.password)
async def reg2(message: Message, state:FSMContext):
    await state.update_data(password=message.text)
    data =await state.get_data()

    datafromdb = await get_password_db(data["password"])

    if datafromdb == True:
        await del_password_db(data["password"])
        await add_user_db(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        await message.answer(f'Успешно зарегистрировались', parse_mode=ParseMode.HTML)
        # Создаем объект для фотографии
        photo = FSInputFile("image/emall-logo.png")

        # Определяем текст сообщения
        welcome_text = (
            f"👋 <b>Добро пожаловать!</b>\n\n"
            f"Это корпоративный бот {ULNAME}.\n\n"
            f"Бот может уведомлять Вас о новых заказах на маркетплейсе Emall."
        )

        # Отправляем фотографию с текстом
        await message.answer_photo(photo=photo, caption=welcome_text, parse_mode=ParseMode.HTML)
        await message.answer(f"Воспользуйтесь клавиатурой",
                             reply_markup=await menu_keyboard_inline_1(message.from_user.id), parse_mode=ParseMode.HTML)


    else:
        await message.answer(f'Неправильный пароль. Обратитесь к администратору или попробуйте еще раз: ', reply_markup=start_keyboard_inline, parse_mode=ParseMode.HTML)
    await state.clear()



@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Это команда /help', parse_mode=ParseMode.HTML)


@router.message(Command('about'))
async def cmd_about(message: Message):
    await message.answer('<b>Алексей\n<a href="tel:+375297047262">+375-29-704-72-62</a></b>', parse_mode=ParseMode.HTML)



@router.message(Command('alexkarden'))
async def cmd_alexkarden(message: Message):
    await message.answer('<b>Алексей\n<a href="tel:+375297047262">+375-29-704-72-62</a></b>', parse_mode=ParseMode.HTML)













@router.message()
async def all_message(message: Message):
    text = message.text
    if text =='⚙️ Меню':
        await message.answer(f"Как часто вы хотите получать уведомления о курсах валют в течение дня?\n\n1 раз в день :(14:30)\n3 раза в день :(10:00, 12:30, 15:00)\n\nПри выборе появляется ✅\nДля отмены выбора еще раз нажмите на кнопку.", parse_mode='HTML')
    elif text == 'alexkarden':
        await message.answer('<b>Алексей\n<a href="tel:+375297047262">+375-29-704-72-62</a></b>', parse_mode='HTML')



@router.callback_query()
async def callback_query(callback: CallbackQuery, state:FSMContext):
    # Получаем данные из обратного запроса
    data = callback.data
    # Обрабатываем данные
    if data == 'menu1' or data == 'menu112' or data == 'menu121' :
        await callback.answer()
        await callback.message.edit_text(f"Это меню, доступное администраторам, для управления пользователями. Можно генерировать инвайты для новых пользователей, просматривать и удалять существующих пользователей.", reply_markup=menu_keyboard_inline_11, parse_mode='HTML')
    elif data == 'menu11' or data == 'menu111':
        await callback.answer()
        await callback.message.edit_text(f"Перешлите это сообщение пользователю, который будет получать уведомления о новых заказах.\n\n"
                                         f"Инструкция по подключению\n\n"
                                         f"1. Кликните по боту {BOTNAME} \n"
                                         f"2. Для регистрации используйте следующий пароль:\n"
                                         f"<i>(По клику копируется пароль в буфер)</i>\n"
                                         f" <code>{await add_password_db()}</code>\n\n"
                                         f"Это одноразовый пароль, который действует 10 минут. Если Вы не успели зарегистрироваться, запросите у администратора новый пароль.", reply_markup=menu_keyboard_inline_111,  parse_mode='HTML')


    elif data == 'menu12':
        await callback.answer()
        await callback.message.edit_text(f"Здесь можно просматривать и удалять пользователей", reply_markup=menu_keyboard_inline_121,  parse_mode='HTML')

    elif data == 'menu13' or data == 'menu26' or data == 'menu31':
        await callback.answer()
        await callback.message.edit_text(f"Здесь можно просматривать и удалять пользователей", reply_markup=await menu_keyboard_inline_1(callback.message.chat.id),  parse_mode='HTML')

    elif data == 'menu2':
        await callback.answer()
        await callback.message.edit_text(f"Здесь можно просматривать и настраивать уведомления", reply_markup=await create_dynamic_keyboard_select(callback.message.chat.id,'none','none'),  parse_mode='HTML')




    elif data == 'menu3':
        await callback.answer()
        await callback.message.edit_text(f"Здесь можно просматривать и удалять пользователей",
                                         reply_markup=menu_keyboard_inline_3, parse_mode='HTML')

    elif data == 'menu4':
        # Удаляем сообщение с клавиатурой
        await callback.answer()
        await callback.message.edit_text(f"Бот настроен и работает",  parse_mode='HTML')


    elif data == 'full':
        # Удаляем сообщение с клавиатурой
        await callback.answer()
        await callback.message.edit_text(f"Вы будете получать полное уведомления о новом заказе с фото товара", reply_markup=await create_dynamic_keyboard_select(callback.from_user.id, 'full','none'),  parse_mode='HTML')

    elif data == 'short':
        # Удаляем сообщение с клавиатурой
        await callback.answer()
        await callback.message.edit_text(f"Вы будете получать сокращенное текстовое уведомление о новом заказе", reply_markup=await create_dynamic_keyboard_select(callback.from_user.id, 'short','none'),  parse_mode='HTML')


    elif data == 'never':
        # Удаляем сообщение с клавиатурой
        await callback.answer()
        await callback.message.edit_text(f"Вы отключили уведомления и не будете получать уведомления о новом заказе", reply_markup=await create_dynamic_keyboard_select(callback.from_user.id, 'none','never'),  parse_mode='HTML')

    elif data == 'alltime':
        # Удаляем сообщение с клавиатурой
        await callback.answer()
        await callback.message.edit_text(f"Вы будете получать уведомление о новом заказе в любое время суток", reply_markup=await create_dynamic_keyboard_select(callback.from_user.id, 'none','alltime'),  parse_mode='HTML')

    elif data == 'worktime':
        # Удаляем сообщение с клавиатурой
        await callback.answer()
        await callback.message.edit_text(f"Вы будете получать уведомление о новом заказе в рабочее время с понедельника по пятницу с 09:00 по 18:00", reply_markup=await create_dynamic_keyboard_select(callback.from_user.id, 'none','worktime'),  parse_mode='HTML')


    elif data == 'pasword':
        # Удаляем сообщение с клавиатурой
        await callback.message.delete()
        await state.set_state(Reg.password)
        await callback.message.answer('Введите пароль', parse_mode=ParseMode.HTML)