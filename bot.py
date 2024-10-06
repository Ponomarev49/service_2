import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram import Router

from check_position import calculate_distance
from read import read_users, read_workplaces, Coordinates

logging.basicConfig(level=logging.INFO)
bot = Bot(token="6853655201:AAH8uFGgzkuF6TA3-Tlim6IW8U995ukgllE")
dp = Dispatcher()
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


async def main():
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


@router.message(F.location)
async def handle_location(message: types.Message):
    user_id = message.from_user.username
    latitude = message.location.latitude
    longitude = message.location.longitude
    answer = calculate_distance(workplaces_dict[int(users_dict[user_id])], Coordinates([latitude, longitude]))
    await message.reply(f"{answer}")


if __name__ == "__main__":
    users_dict = read_users()
    workplaces_dict = read_workplaces()
    asyncio.run(main())
