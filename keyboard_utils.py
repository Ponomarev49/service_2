from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

def create_main_keyboard():
    change_phone = KeyboardButton(text="Сменить телефон")
    change_work = KeyboardButton(text="Сменить место работы")
    check_work = KeyboardButton(text="Проверить на работе")
    set_schedule = KeyboardButton(text="Изменить расписание")

    return ReplyKeyboardMarkup(
        keyboard=[[change_phone, change_work, check_work, set_schedule]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def create_phone_keyboard():
    phone_button = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    return ReplyKeyboardMarkup(
        keyboard=[[phone_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def create_location_keyboard():
    location_button = KeyboardButton(text="Отправить геолокацию", request_location=True)
    return ReplyKeyboardMarkup(
        keyboard=[[location_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def create_dates_buttons(username, employees_db, bot, state: FSMContext):
    id = employees_db.check_user_by_username(username)["user_id"]
    nearest_days = employees_db.get_employee_next_dates(username)

    buttons = []
    response_text = "Следующие 10 дней:\nНажмите на дату, чтобы изменить\n\n"

    for key, value in nearest_days.items():
        buttons.append(
            [InlineKeyboardButton(text=f"{key} - {value}", callback_data=f"{username}:{key}:{value}")])

    # Кнопка для отправки выбранных
    buttons.append([InlineKeyboardButton(text="Сохранить", callback_data="save_schedule")])

    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    sent_message = await bot.send_message(id, response_text, reply_markup=inline_kb)

    # Сохраняем ID сообщения, которое нужно будет удалить позже
    await state.update_data(sent_message_id=sent_message.message_id)

    return inline_kb