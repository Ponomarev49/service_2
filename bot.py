import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import os
from dotenv import load_dotenv

from calc_distance import calculate_distance, Coordinates
from db_api_connector import stores_db_connector, employees_db_connector

COORDINATES_ERROR = 0.05

load_dotenv()

token = os.getenv("token")
DB_CONNECTION_PARAMS: tuple[str, str] = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())


class LocationStates(StatesGroup):
    set_workplace = State()  # Для установки рабочего места
    check_on_work = State()  # Для проверки, находится ли пользователь на рабочем месте
    change_phone = State()  # Для изменения номера телефона


def create_main_keyboard():
    change_phone = (KeyboardButton(text="Сменить телефон"))
    change_work = (KeyboardButton(text="Сменить место работы"))
    check_work = (KeyboardButton(text="Проверить на работе"))

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[change_phone, change_work, check_work]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def create_phone_keyboard():
    phone_button = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[phone_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def create_location_keyboard():
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
    if employees_db_connector.check_user_by_username(username):
        await message.answer("Добро пожаловать обратно!", reply_markup=create_main_keyboard())
    else:
        await message.answer(
            "Мы не нашли вас в базе данных. Пожалуйста, отправьте ваш номер телефона:",
            reply_markup=create_phone_keyboard()
        )


# Сменить место работы
@dp.message(F.text == "Сменить место работы")
async def handle_change_work(message: types.Message, state: FSMContext):
    await message.answer("Отправьте вашу геолокацию для выбора нового места работы:",
                         reply_markup=create_location_keyboard())
    await state.set_state(LocationStates.set_workplace)


# Проверить на работе
@dp.message(F.text == "Проверить на работе")
async def handle_check_work(message: types.Message, state: FSMContext):
    username = message.from_user.username
    store_id = employees_db_connector.get_employee_workplace_coordinates(username)
    coordinates = stores_db_connector.get_store_coordinates_by_id(store_id)
    store_lat, store_lon = coordinates["lat"], coordinates["lon"]

    await state.update_data(store_lat=store_lat, store_lon=store_lon)
    await message.answer(
        "Отправьте вашу текущую геолокацию, чтобы проверить, находитесь ли вы на рабочем месте:",
        reply_markup=create_location_keyboard()
    )
    await state.set_state(LocationStates.check_on_work)


# Сменить номер телефона
@dp.message(F.text == "Сменить телефон")
async def handle_change_phone(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, отправьте ваш номер телефона:", reply_markup=create_phone_keyboard()
    )
    await state.set_state(LocationStates.change_phone)


@dp.message(F.contact)
async def contact_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    phone_number = message.contact.phone_number
    username = message.from_user.username

    # Если пользователь отправляет геолокацию для установки рабочего места
    if current_state == LocationStates.change_phone:
        employees_db_connector.update_user_phone(username, phone_number)
        await message.answer(f"Номер успешно изменен: {phone_number}", reply_markup=create_main_keyboard())
    else:
        if not employees_db_connector.check_user_by_username(username):
            employees_db_connector.add_user_to_db(username, phone_number)
            await message.answer("Пожалуйста, отправьте вашу геолокацию:", reply_markup=create_location_keyboard())
            await state.set_state(LocationStates.set_workplace)


@dp.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    # Если пользователь отправляет геолокацию для установки рабочего места
    if current_state == LocationStates.set_workplace:
        user_lat = message.location.latitude
        user_lon = message.location.longitude

        nearest_stores = stores_db_connector.get_nearest_stores_for_user(user_lat, user_lon)
        buttons = []
        response_text = "Три ближайших магазина:\n\n"

        for distance, store_id, name, lat, lon, city, line1 in nearest_stores:
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
            await message.answer("Вы находитесь на рабочем месте.", reply_markup=create_main_keyboard())
        else:
            await message.answer("Вы не находитесь на рабочем месте.", reply_markup=create_main_keyboard())
    await state.clear()


@dp.callback_query(F.data.startswith('select_store_'))
async def process_store_selection(callback_query: types.CallbackQuery):
    store_id = int(callback_query.data.split('_')[-1])
    employees_db_connector.update_user_store_id(username=callback_query.from_user.username, store_id=store_id)
    await callback_query.message.answer(f"Вы успешно авторизованы. Ваше рабочее место {store_id}",
                                        reply_markup=create_main_keyboard())


async def main():
    stores_db_connector.connect(*DB_CONNECTION_PARAMS)
    employees_db_connector.connect(*DB_CONNECTION_PARAMS)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
