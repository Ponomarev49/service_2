from apscheduler.triggers.cron import CronTrigger
from datetime import time, datetime, timedelta, timezone
from utils import send_message, send_false_message, update_schedule

# Планирование задач для каждого пользователя
def workday_messages(scheduler, employees_db, stores_db, attendance_db, bot):
    employees = employees_db.get_all_users()
    for employee in employees:
        status =next(iter(employees_db.get_employee_next_dates(employee["username"]).items()))[1]

        if status=="Работаю":
            # _, employee_id, _ = employee.values()
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
                                            microsecond=0) - offset_delta) + timedelta(minutes=2)
            
            work_start2_utc = (now_utc.replace(hour=work_start_time.hour, 
                                            minute=work_start_time.minute, 
                                            second=work_start_time.second, 
                                            microsecond=0) - offset_delta) + timedelta(minutes=4)
            
            work_end_utc = (now_utc.replace(hour=work_end_time.hour, 
                                            minute=work_end_time.minute, 
                                            second=work_end_time.second, 
                                            microsecond=0) - offset_delta) - timedelta(minutes=2)
            
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


# ежедневное обновление десяти предстоящих дат в базе данных
def everyday_update_dates(employees_db):
    all_users = employees_db.get_all_users()
    for user in all_users:
        username, _, _ = user.values()
        user_dates = employees_db.get_employee_next_dates(username)
        updates_user_dates = update_schedule(user_dates)
        employees_db.update_employee_next_dates(username, updates_user_dates)


# добавление задачи обновления дат в scheduler
def add_update_dates_job(scheduler, employees_db):
    scheduler.add_job(
        everyday_update_dates,
        CronTrigger(hour=21, minute=00, timezone=timezone.utc),
        args=[employees_db],
        id="update_dates",
        replace_existing=True
    )