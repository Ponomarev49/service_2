from datetime import datetime, timedelta

def get_next_10_days_formatted():
    today = datetime.today()
    next_10_days = [(today + timedelta(days=i)).strftime('%d.%m.%Y') for i in range(1, 11)]
    return next_10_days


async def send_message(user_id, bot, message):
    await bot.send_message(user_id, message)


async def send_false_message(user_id, bot, message, time, attendance_db):
    attendance_db.add_attendance(user_id, datetime.now().strftime("%Y.%m.%d"), str(time), False)
    await bot.send_message(user_id, message)



def update_schedule(schedule):
    # Получаем отсортированные даты
    dates = list(schedule.keys())
    
    # Удаляем первый день
    del schedule[dates[0]]
    
    # Определяем последний день и добавляем новый
    last_date = datetime.strptime(dates[-1], "%d.%m.%Y")
    next_date = last_date + timedelta(days=1)
    schedule[next_date.strftime("%d.%m.%Y")] = "Работаю"
    
    return schedule