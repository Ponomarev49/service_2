# import sqlite3
# import json
#
# # Подключение к базе данных (используем ту же базу данных)
# connection = sqlite3.connect('data/employees.db')
# cursor = connection.cursor()
#
# # Создание таблицы работников
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS employees (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT NOT NULL,
#     store_id INTEGER,
#     FOREIGN KEY (store_id) REFERENCES stores(id)
# )
# ''')
#
# # Сохраняем изменения
# connection.commit()
# print("Таблица работников создана успешно.")
#
# # Закрытие соединения
# connection.close()
#
#
# def read_workplaces():
#     with open("data/stores.json", 'r') as file:
#         data = json.load(file)
#     return data
#
#
# # Подключение к базе данных
# connection = sqlite3.connect('data/stores.db')
# cursor = connection.cursor()
#
# # Создание таблицы, если она не существует
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS stores (
#     id INTEGER PRIMARY KEY,
#     name TEXT,
#     lat REAL,
#     lon REAL,
#     city TEXT,
#     line1 TEXT,
#     line2 TEXT,
#     code TEXT
# )
# ''')
# connection.commit()
#
# # Вставка данных из массива
# for data in read_workplaces():
#     cursor.execute('''
#     INSERT INTO stores (id, name, lat, lon, city, line1, line2, code)
#     VALUES (:id, :name, :lat, :lon, :city, :line1, :line2, :code)
#     ''', data)
#
# # Сохраняем изменения
# connection.commit()
# print("Все данные успешно добавлены.")
#
# # Проверка вставленных данных
# cursor.execute("SELECT * FROM stores")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)
#
# # Закрытие соединения
# connection.close()
#
#
# def print_all_rows():
#     with sqlite3.connect("data/employees.db") as connection:
#         cursor = connection.cursor()
#         rows = cursor.execute(f"SELECT * FROM employees").fetchall()
#
#         if rows:
#             for row in rows:
#                 print(row)
#         else:
#             print(f"Таблица employees пуста.")
#
# print_all_rows()
