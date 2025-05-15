from database.db_api_connector import DBAPIConnector

class EmployeeAttendanceDBConnector(DBAPIConnector):
    table_name: str = "EmployeeAttendance"

    id: int = "id"
    user_id: int = "user_id"
    date: str = "date"
    time: str = "time"
    was_present: bool = "was_present"

    def add_attendance(self, user_id: int, date: str, time: str, was_present: bool):
        # Добавление метки
        self.supabase.table(self.table_name).insert(
            {self.user_id: user_id, self.date: date, self.time: time, self.was_present: was_present}).execute()
        print(f"Добавлена метка {user_id} {time} {was_present}.")