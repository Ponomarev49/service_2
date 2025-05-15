from database.db_api_connector import DBAPIConnector

class EmployeesDBConnector(DBAPIConnector):
    table_name: str = "Employees"

    user_id: int = "user_id"
    username: str = "username"
    store_id: int = "store_id"
    phone_number: str = "phone_number"
    nearest_dates: dict = "nearest_dates"

    def add_user(self, username: str, user_id: int):
        # Добавление нового пользователя
        self.supabase.table(self.table_name).insert(
            {self.username: username, self.user_id: user_id}).execute()
        print(f"Добавлен пользователь {username} с ID {user_id}.")

    def check_user_by_username(self, username: str):
        # Подключение к базе данных и выполнение запроса
        response = self.supabase.table(self.table_name).select("*").eq(self.username, username).execute()
        response_data = response.data
        if response_data:
            return response_data[0]
        return {}

    def add_phone_number_to_user(self, username: str, phone_number: str):
        # Добавление телефона пользователя
        self.supabase.table(self.table_name).update({self.phone_number: phone_number}).eq(self.username,
                                                                                          username).execute()
        print(f"Пользователь {username} установил номер телефона {phone_number}.")

    def update_user_store_id(self, username: str, store_id: int):
        # Обновление store_id для пользователя
        self.supabase.table(self.table_name).update({self.store_id: store_id}).eq(self.username, username).execute()
        print(f"Пользователь {username} установил магазин с ID {store_id}.")

    def get_employee_workplace(self, username: str):
        # Получаем store_id сотрудника
        response = self.supabase.table(self.table_name).select("store_id").eq(self.username, username).execute()
        response_data = response.data
        if response_data:
            store_id = response_data[0]['store_id']
            # Получаем координаты магазина по store_id
            return store_id
        return {}

    def get_all_users(self):
        # получаем username и store_id всех сотрудников
        response = self.supabase.table(self.table_name).select("username", "user_id", "store_id").execute()
        response_data = response.data
        if response_data:
            return response_data
        return []

    def get_employee_next_dates(self, username: str):
        response = self.supabase.table(self.table_name).select("nearest_dates").eq(self.username, username).execute()
        response_data = response.data
        return response_data[0]["nearest_dates"]

    def update_employee_next_dates(self, username: str, dates: dict):
        self.supabase.table(self.table_name).update({self.nearest_dates: dates}).eq(self.username, username).execute()
