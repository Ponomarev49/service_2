from datetime import datetime, timedelta

def get_next_10_days_formatted():
    today = datetime.today()
    next_10_days = [(today + timedelta(days=i)).strftime('%d.%m.%Y') for i in range(1, 11)]
    return next_10_days

# Функция для отправки сообщений
async def send_message(user_id, bot, message):
    # Отправляем сообщение
    await bot.send_message(user_id, message)