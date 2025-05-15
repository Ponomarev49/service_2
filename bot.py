import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.stores_db_connector import StoresDBConnector
from database.employees_db_connector import EmployeesDBConnector
from database.employee_attendance_db_connector import EmployeeAttendanceDBConnector
from utils import scheduler_handler
from core.handlers import register_handlers

load_dotenv()

token = os.getenv("token")
DB_CONNECTION_PARAMS = (os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


async def main():
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    stores_db_connector = StoresDBConnector()
    employees_db_connector = EmployeesDBConnector()
    employee_attendance_db_connector = EmployeeAttendanceDBConnector()

    stores_db_connector.connect(*DB_CONNECTION_PARAMS)
    employees_db_connector.connect(*DB_CONNECTION_PARAMS)
    employee_attendance_db_connector.connect(*DB_CONNECTION_PARAMS)

    scheduler = AsyncIOScheduler()
    scheduler.start()

    register_handlers(dp, bot, scheduler, stores_db_connector, employees_db_connector, employee_attendance_db_connector)

    scheduler_handler.workday_messages(scheduler, employees_db_connector, stores_db_connector, employee_attendance_db_connector, bot)
    scheduler_handler.everyday_update(scheduler, employees_db_connector, stores_db_connector, employee_attendance_db_connector, bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
