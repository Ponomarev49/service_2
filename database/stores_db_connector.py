from utils.location_handler import calculate_distance, Coordinates
from database.db_api_connector import DBAPIConnector

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
    workTimeStart: str = "workTimeStart"
    workTimeEnd: str = "workTimeEnd"
    timezone: str = "timezone"

    def get_nearest_stores_for_user(self, user_lat: float, user_lon: float):
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

    def get_store_coordinates_by_id(self, id: int):
        # Получаем координаты магазина по его ID
        response = self.supabase.table(self.table_name).select("lat, lon").eq(self.id, id).execute()
        result = response.data
        if result:
            return result[0]
        return {}

    def get_time_for_store(self, id: int):
        # Получаем часовой пояс магазина
        response = self.supabase.table(self.table_name).select("city", "workTimeStart", "workTimeEnd", "timezone").eq(self.id,
                                                                                                     id).execute()
        result = response.data
        if result:
            return result[0]
        return {}