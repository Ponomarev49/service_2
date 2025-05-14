from aiogram.fsm.state import StatesGroup, State

class LocationStates(StatesGroup):
    set_workplace = State()  # Для установки рабочего места
    check_on_work = State()  # Для проверки, находится ли пользователь на рабочем месте
    change_phone = State()  # Для изменения номера телефона