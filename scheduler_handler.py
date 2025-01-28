from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
from utils import send_message


# Планирование задач для каждого пользователя
def schedule_messages(scheduler, employees_db, stores_db, bot):
    employees = employees_db.get_all_users()
    for employee in employees:
        _, employee_id, _ = employee.values()
        employee_city, employee_work_time_start, employee_timezone = stores_db.get_timezone_and_start_for_user(
            employee["store_id"]).values()

        # Преобразуем строку времени в объект time
        employee_work_time_start = datetime.strptime(employee_work_time_start, "%H:%M:%S").time()
        employee_timezone = datetime.strptime(employee_timezone, "%H:%M:%S").time()

        # Вычисляем разницу
        delta = timedelta(hours=employee_work_time_start.hour, minutes=employee_work_time_start.minute,
                        seconds=employee_work_time_start.second) - \
                timedelta(hours=employee_timezone.hour, minutes=employee_timezone.minute,
                        seconds=employee_timezone.second)

        total_seconds = int(delta.total_seconds())
        if delta.days == -1:
            total_seconds += 24 * 60 * 60

        # Планируем задачу
        scheduler.add_job(
            send_message,
            CronTrigger(hour=total_seconds // 3600, minute=(total_seconds % 3600) // 60, timezone=timezone.utc),
            args=[employee_id, bot,
                f"Сообщение отправлено в {employee_work_time_start} по вашему времени\nПривет из {employee_city}"],
            id=f"message_{employee_id}",
            replace_existing=True
        )