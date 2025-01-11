from supabase import create_client, Client

from calc_distance import calculate_distance, Coordinates


class DBAPIConnector:
    supabase: Client

    def connect(self, supabase_url: str, supabase_key: str) -> None:
        self.supabase = create_client(supabase_url, supabase_key)


class StoresDBConnector(DBAPIConnector):
    table_name: str = "Stores"

    id: int = "id"
    name: str = "name"
    city: str = "city"
    address: str = "address"
    lat: str = "lat"
    lon: str = "lon"
    code: str = "code"
    chat: str = "chat"
    timezone: str = "timezone"
    workTimeStart: str = "workTimeStart"
    workTimeEnd: str = "workTimeEnd"

    def get_nearest_stores_for_user(self, user_lat: float, user_lon: float) -> list:
        # Получаем все магазины
        response = self.supabase.table(self.table_name).select("*").execute()
        stores = response.data

        store_distances = []
        for store in stores:
            store_id, name, lat, lon, city, address = store['id'], store['name'], store['lat'], store['lon'], \
                store['city'], store['address']
            # Расчет расстояния между пользователем и магазином
            distance = calculate_distance(Coordinates([user_lat, user_lon]), Coordinates([lat, lon]))
            store_distances.append((distance, store_id, name, lat, lon, city, address))

        store_distances.sort()  # Сортируем по расстоянию
        return store_distances[:3]  # Возвращаем топ 3 ближайших магазина


    def get_store_coordinates_by_id(self, id: int) -> dict:
        # Получаем координаты магазина по его ID
        response = self.supabase.table(self.table_name).select("lat, lon").eq(self.id, id).execute()
        result = response.data
        if result:
            return result[0]
        return {}


class EmployeesDBConnector(DBAPIConnector):
    table_name: str = "Employees"

    id: int = "id"
    username: str = "username"
    store_id: int = "store_id"
    phone_number: str = "phone_number"

    def check_user_by_username(self, username: str) -> dict:
        # Подключение к базе данных и выполнение запроса
        response = self.supabase.table(self.table_name).select("*").eq(self.username, username).execute()
        response_data = response.data
        if response_data:
            return response_data[0]
        return {}

    def add_user_to_db(self, username: str, phone_number: str):
        # Вставка нового пользователя в таблицу
        self.supabase.table(self.table_name).insert(
            {self.username: username, self.phone_number: phone_number}).execute()
        print(f"Пользователь {username} добавлен с номером {phone_number}.")

    def update_user_store_id(self, username: str, store_id: int):
        # Обновление store_id для пользователя
        self.supabase.table(self.table_name).update({self.store_id: store_id}).eq(self.username, username).execute()
        print(f"Пользователь {username} установил магазин с ID {store_id}.")

    def update_user_phone(self, username: str, phone_number: str):
        # Обновление номера телефона для пользователя
        self.supabase.table(self.table_name).update({self.phone_number: phone_number}).eq(self.username,
                                                                                          username).execute()
        print(f"Пользователь {username} измененил номер телефона на {phone_number}.")

    def get_employee_workplace_coordinates(self, username: str) -> dict:
        # Получаем store_id сотрудника
        response = self.supabase.table(self.table_name).select("store_id").eq(self.username, username).execute()
        result = response.data
        if result:
            store_id = result[0]['store_id']
            # Получаем координаты магазина по store_id
            return store_id
        return {}


stores_db_connector = StoresDBConnector()
employees_db_connector = EmployeesDBConnector()
