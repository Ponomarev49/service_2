import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from calc_distance import calculate_distance, Coordinates

COORDINATES_ERROR = 0.01

bot = Bot(token="")
dp = Dispatcher()


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
def add_user_to_db(username, store_id):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO employees (username, store_id) VALUES (?, ?)", (username, store_id))
    connection.commit()
    connection.close()


def get_nearest_stores_for_user(user_lat, user_lon):
    connection = get_connection_to_stores_db()
    cursor = connection.cursor()

    # Получаем все магазины из базы данных
    cursor.execute("SELECT id, name, lat, lon, city, line1, line2, code FROM stores")
    stores = cursor.fetchall()
    connection.close()

    # Считаем расстояние до каждого магазина и сохраняем его в списке
    store_distances = []
    for store in stores:
        store_id, name, lat, lon, city, line1, line2, code = store
        distance = calculate_distance(Coordinates([user_lat, user_lon]), Coordinates([lat, lon]))
        store_distances.append((distance, store_id, name, lat, lon, city, line1, line2, code))

    # Сортируем магазины по расстоянию и выбираем три ближайших
    store_distances.sort()
    return store_distances[:3]


# Функция для получения координат рабочего места сотрудника по его username
def get_employee_workplace_id(username):
    connection = get_connection_to_workers_db()
    cursor = connection.cursor()

    # Получаем id_workplace для сотрудника
    cursor.execute("""
        SELECT store_id
        FROM employees
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()
    connection.close()

    connection = get_connection_to_stores_db()
    cursor = connection.cursor()

    # Получаем координаты магазина по его id
    cursor.execute("""
        SELECT lat, lon
        FROM stores
        WHERE id = ?
    """, (result[0],))

    result = cursor.fetchone()
    connection.close()

    return result


# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.username

    # Проверяем, есть ли пользователь в базе данных по username
    user = check_user_by_username(username)

    if user:
        await message.reply("Добро пожаловать! Вы уже авторизованы")
    else:
        await message.reply("Добро пожаловать! Вы не авторизованы. Пожалуйста, отправьте вашу геопозицию")


# Обработчик команды /on_work
@dp.message(Command("on_work"))
async def on_work_command(message: types.Message):
    await message.answer("Отправьте вашу геопозицию для проверки.")


# Обработчик для получения геопозиции и поиска ближайших магазинов
@dp.message(F.location)
async def location_handler(message: types.Message):
    if message.location:
        user_lat = message.location.latitude
        user_lon = message.location.longitude


        if check_user_by_username(message.from_user.username):
            # Получаем координаты магазина, в котором работает пользователь
            store_coords = get_employee_workplace_id(message.from_user.username)
            store_lat, store_lon = store_coords
            distance = calculate_distance(Coordinates([user_lat, user_lon]), Coordinates([store_lat, store_lon]))

            if distance <= COORDINATES_ERROR:
                await message.answer("Вы находитесь на рабочем месте.")
            else:
                await message.answer("Вы находитесь слишком далеко от рабочего места.")

        else:
            # Получаем три ближайших магазина
            nearest_stores = get_nearest_stores_for_user(user_lat, user_lon)

            # Создаем inline-клавиатуру с кнопками для выбора магазина
            buttons = []
            response_text = "Вот три ближайших магазина:\n\n"

            for distance, store_id, name, lat, lon, city, line1, line2, code in nearest_stores:
                response_text += (f"🏬 {name}\n📍 Адрес: {line1}, {city}\n"
                                  f"📏 Расстояние: {distance:.2f} км\n\n")
                buttons.append(
                    [InlineKeyboardButton(text=f"Выбрать: {name}", callback_data=f"select_store_{store_id}")])

            inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)

            await message.answer(response_text, reply_markup=inline_kb)


# Обработчик для выбора магазина из предложенных
@dp.callback_query(F.data.startswith('select_store_'))
async def process_store_selection(callback_query: types.CallbackQuery):
    store_id = int(callback_query.data.split('_')[-1])

    # Добавляем нового работника в базу данных
    add_user_to_db(username=callback_query.from_user.username, store_id=store_id)

    await callback_query.answer(f"Магазин с ID {store_id} выбран.")
    await callback_query.message.reply("Вы выбрали магазин. Спасибо!")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
