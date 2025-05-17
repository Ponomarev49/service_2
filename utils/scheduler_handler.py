from apscheduler.triggers.cron import CronTrigger
from datetime import time, datetime, timedelta, timezone, date
from utils.utils import send_message, send_false_message, update_schedule
from .constants import DELTA

# Планирование задач для каждого пользователя
def workday_messages(scheduler, employees_db, stores_db, attendance_db, bot):
    employees = employees_db.get_all_users()
    for employee in employees:
        if employee["store_id"]:
            message_for_one_user(employee, employees_db, stores_db, attendance_db, scheduler,  bot)


def message_for_one_user(employee, employees_db, stores_db, attendance_db, scheduler,  bot):
    next_dates = employees_db.get_employee_next_dates(employee["username"])
    today_str = date.today().strftime('%d.%m.%Y')

    if today_str in next_dates and next_dates[today_str] == "Работаю":
            employee_city, employee_work_time_start, employee_work_time_end, employee_timezone = stores_db.get_time_for_store(
                employee["store_id"]).values()

            # Преобразуем строковые времена в объекты datetime.time
            work_start_time = datetime.strptime(employee_work_time_start, "%H:%M:%S").time()
            work_end_time = datetime.strptime(employee_work_time_end, "%H:%M:%S").time()
            timezone_offset = datetime.strptime(employee_timezone, "%H:%M:%S").time()

            # Преобразуем смещение в timedelta
            offset_delta = timedelta(hours=timezone_offset.hour, minutes=timezone_offset.minute, seconds=timezone_offset.second)

            # Текущее время в UTC
            now_utc = datetime.now(timezone.utc)

            # Вычисляем UTC-время для отправки
            work_start_utc = (now_utc.replace(hour=work_start_time.hour, 
                                            minute=work_start_time.minute, 
                                            second=work_start_time.second, 
                                            microsecond=0) - offset_delta) + timedelta(minutes=DELTA)
            
            work_start2_utc = (now_utc.replace(hour=work_start_time.hour, 
                                            minute=work_start_time.minute, 
                                            second=work_start_time.second, 
                                            microsecond=0) - offset_delta) + timedelta(minutes=2*DELTA)
            
            work_end_utc = (now_utc.replace(hour=work_end_time.hour, 
                                            minute=work_end_time.minute, 
                                            second=work_end_time.second, 
                                            microsecond=0) - offset_delta) - timedelta(minutes=DELTA)
            
            work_end2_utc = now_utc.replace(hour=work_end_time.hour, 
                                            minute=work_end_time.minute, 
                                            second=work_end_time.second, 
                                            microsecond=0) - offset_delta
            
            add_work_job(scheduler, work_start_utc.hour, work_start_utc.minute, employee["user_id"], bot, "start")
            add_work_job_false(scheduler, work_start2_utc.hour, work_start2_utc.minute, employee["user_id"], bot, "start2", attendance_db)
            add_work_job(scheduler, work_end_utc.hour, work_end_utc.minute, employee["user_id"], bot, "end")
            add_work_job_false(scheduler, work_end2_utc.hour, work_end2_utc.minute, employee["user_id"], bot, "end2", attendance_db)


def add_work_job(scheduler, hour, minute, employee_id, bot, text):
    # Планируем задачу
    scheduler.add_job(
        send_message,
        CronTrigger(hour=hour, minute=minute, timezone=timezone.utc),
        args = [employee_id, bot,"Не забудьте отметить свое присутствие на работе!"],
        id = f"job_{text}_{employee_id}",
        replace_existing = True
    )


def add_work_job_false(scheduler, hour, minute, employee_id, bot, text, attendance_db):
    # Планируем задачу
    scheduler.add_job(
        send_false_message,
        CronTrigger(hour=hour, minute=minute, timezone=timezone.utc),
        args = [employee_id, bot, "Вы не отметились вовремя", time(hour=hour, minute=minute), attendance_db],
        id = f"job_{text}_{employee_id}",
        replace_existing = True
    )


def remove_work_job(scheduler, work_time, user_id):
    if scheduler.get_job(f"job_{work_time}_{user_id}"):
        scheduler.remove_job(f"job_{work_time}_{user_id}")
    if scheduler.get_job(f"job_{work_time}2_{user_id}"):
        scheduler.remove_job(f"job_{work_time}2_{user_id}")


def remove_all_work_job_for_user(scheduler, user_id):
    for work_time in ["start", "end"]:
        remove_work_job(scheduler, work_time, user_id)


def update_jobs_for_user(username, scheduler, employees_db, stores_db, attendance_db, bot):
    employee = employees_db.check_user_by_username(username)
    remove_all_work_job_for_user(scheduler, employee["user_id"])
    message_for_one_user(employee, employees_db, stores_db, attendance_db, scheduler,  bot)


# ежедневное обновление десяти предстоящих дат в базе данных
def everyday_workday_update(scheduler, employees_db, stores_db, attendance_db, bot):
    all_users = employees_db.get_all_users()
    for user in all_users:
        username, _, _ = user.values()
        user_dates = employees_db.get_employee_next_dates(username)
        updates_user_dates = update_schedule(user_dates)
        employees_db.update_employee_next_dates(username, updates_user_dates)

    workday_messages(scheduler, employees_db, stores_db, attendance_db, bot)


# добавление задачи обновления дат в scheduler
def everyday_update(scheduler, employees_db, stores_db, attendance_db, bot):
    scheduler.add_job(
        everyday_workday_update,
        CronTrigger(hour=21, minute=00, timezone=timezone.utc),
        args=[scheduler, employees_db, stores_db, attendance_db, bot],
        id="update_dates",
        replace_existing=True
    )