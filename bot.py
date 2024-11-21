import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import os
from dotenv import load_dotenv

from calc_distance import calculate_distance, Coordinates

COORDINATES_ERROR = 0.05

load_dotenv()

token = os.getenv("token")
bot = Bot(token = token)
dp = Dispatcher(storage=MemoryStorage())


class LocationStates(StatesGroup):
    set_workplace = State()  # Для установки рабочего места
    check_on_work = State()  # Для проверки, находится ли пользователь на рабочем месте
    change_phone = State()  # Для изменения номера телефона


def get_connection_to_stores_db():
    return sqlite3.connect('data/stores.db')


def get_connection_to_workers_db():
    return sqlite3.connect('data/employees.db')


# Проверка наличия пользователя по username в базе данных
def check_user_by_username(username):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()
    return user


# Функция для добавления нового пользователя
def add_user_to_db(username, phone_number):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO employees (username, phone_number) VALUES (?, ?)", (username, phone_number))
    connection.commit()
    connection.close()
    print(f"Пользователь {username} добавлен с номером {phone_number}.")


# Добавление store_id в бд
def update_user_store_id(username, store_id):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE employees SET store_id = ? WHERE username = ?", (store_id, username))
    connection.commit()
    connection.close()
    print(f"Пользователю {username} установлен магазин с ID {store_id}.")


# Добавление store_id в бд
def update_user_phone(username, phone_number):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE employees SET phone_number = ? WHERE username = ?", (phone_number, username))
    connection.commit()
    connection.close()
    print(f"Пользователю {username} изменен номер телефона на {phone_number}.")


# Получение ближайших магазинов
def get_nearest_stores_for_user(user_lat, user_lon):
    connection = get_connection_to_stores_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, lat, lon, city, line1, line2, code FROM stores")
    stores = cursor.fetchall()
    connection.close()

    store_distances = []
    for store in stores:
        store_id, name, lat, lon, city, line1, line2, code = store
        distance = calculate_distance(Coordinates([user_lat, user_lon]), Coordinates([lat, lon]))
        store_distances.append((distance, store_id, name, lat, lon, city, line1, line2, code))

    store_distances.sort()
    return store_distances[:3]


# Получение координат магазина сотрудника
def get_employee_workplace_coordinates(username):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT store_id
        FROM employees
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()
    connection.close()

    connection = get_connection_to_stores_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT lat, lon
        FROM stores
        WHERE id = ?
    """, (result[0],))

    result = cursor.fetchone()
    connection.close()

    return result


def create_main_keybord():
    change_phone = (KeyboardButton(text="Сменить телефон"))
    change_work = (KeyboardButton(text="Сменить место работы"))
    check_work = (KeyboardButton(text="Проверить на работе"))

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[change_phone, change_work, check_work]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def create_phone_keybord():
    phone_button = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[phone_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def create_location_keybord():
    location_button = KeyboardButton(text="Отправить геолокацию", request_location=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[location_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


@dp.message(Command("start"))
async def start_command(message: types.Message):
    username = message.from_user.username
    if check_user_by_username(username):
        await message.answer("Добро пожаловать обратно!", reply_markup=create_main_keybord())
    else:
        await message.answer(
            "Мы не нашли вас в базе данных. Пожалуйста, отправьте ваш номер телефона:",
            reply_markup=create_phone_keybord()
        )


# Сменить место работы
@dp.message(F.text == "Сменить место работы")
async def handle_change_work(message: types.Message, state: FSMContext):
    await message.answer("Отправьте вашу геолокацию для выбора нового места работы:",
                         reply_markup=create_location_keybord())
    await state.set_state(LocationStates.set_workplace)


# Проверить на работе
@dp.message(F.text == "Проверить на работе")
async def handle_check_work(message: types.Message, state: FSMContext):
    username = message.from_user.username
    coordinates = get_employee_workplace_coordinates(username)
    store_lat, store_lon = coordinates

    await state.update_data(store_lat=store_lat, store_lon=store_lon)
    await message.answer(
        "Отправьте вашу текущую геолокацию, чтобы проверить, находитесь ли вы на рабочем месте:",
        reply_markup=create_location_keybord()
    )
    await state.set_state(LocationStates.check_on_work)


# Сменить номер телефона
@dp.message(F.text == "Сменить телефон")
async def handle_change_phone(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, отправьте ваш номер телефона:", reply_markup=create_phone_keybord()
    )
    await state.set_state(LocationStates.change_phone)


@dp.message(F.contact)
async def contact_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    phone_number = message.contact.phone_number
    username = message.from_user.username

    # Если пользователь отправляет геолокацию для установки рабочего места
    if current_state == LocationStates.change_phone:
        update_user_phone(username, phone_number)
        await message.answer(f"Номер успешно изменен: {phone_number}", reply_markup=create_main_keybord())
    else:
        if not check_user_by_username(username):
            add_user_to_db(username, phone_number)
            await message.answer("Пожалуйста, отправьте вашу геолокацию:", reply_markup=create_location_keybord())
            await state.set_state(LocationStates.set_workplace)


@dp.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # Если пользователь отправляет геолокацию для установки рабочего места
    if current_state == LocationStates.set_workplace:
        user_lat = message.location.latitude
        user_lon = message.location.longitude

        nearest_stores = get_nearest_stores_for_user(user_lat, user_lon)
        buttons = []
        response_text = "Три ближайших магазина:\n\n"

        for distance, store_id, name, lat, lon, city, line1, line2, code in nearest_stores:
            response_text += (f"🏬 {name}\n📍 Адрес: {line1}, {city}\n"
                              f"📏 Расстояние: {distance:.2f} км\n\n")
            buttons.append(
                [InlineKeyboardButton(text=f"Выбрать: {name}", callback_data=f"select_store_{store_id}")])

        inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(response_text, reply_markup=inline_kb)

    # Если пользователь отправляет геолокацию для проверки рабочего места
    elif current_state == LocationStates.check_on_work:
        data = await state.get_data()
        store_lat = data.get("store_lat")
        store_lon = data.get("store_lon")

        user_lat = message.location.latitude
        user_lon = message.location.longitude

        distance = calculate_distance(
            Coordinates([user_lat, user_lon]),
            Coordinates([store_lat, store_lon])
        )

        if distance <= COORDINATES_ERROR:
            await message.answer("Вы находитесь на рабочем месте.", reply_markup=create_main_keybord())
        else:
            await message.answer("Вы не находитесь на рабочем месте.", reply_markup=create_main_keybord())
    await state.clear()


@dp.callback_query(F.data.startswith('select_store_'))
async def process_store_selection(callback_query: types.CallbackQuery):
    store_id = int(callback_query.data.split('_')[-1])
    update_user_store_id(username=callback_query.from_user.username, store_id=store_id)
    await callback_query.message.answer(f"Вы успешно авторизованы. Ваше рабочее место {store_id}",
                                        reply_markup=create_main_keybord())


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
