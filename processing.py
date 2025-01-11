import pandas as pd


def processing_stores(filepath):
    # Чтение DataFrame из JSON-файла
    df = pd.DataFrame(pd.read_json(filepath))

    # удаляем магазины у которых нет координат
    df = df[~(df['lon'].isnull() | (df['lon'] == ""))]
    df = df[~(df['lat'].isnull() | (df['lat'] == ""))]

    # преобразуем тип данных timezone
    timezone = []
    for index, row in df.iterrows():
        timezone.append(row['timezone']['timezone'])
    df['timezone'] = timezone

    # изменяем название столбца
    df.rename(columns={'line1': 'address'}, inplace=True)

    # Удаление слова "Ежедневно с" из столбца "working_hours"
    df['line2'] = df['line2'].str.replace("Ежедневно с ", "", regex=False)

    # Разделение на два столбца: начало и конец работы
    df[['workTimeStart', 'workTimeEnd']] = df['line2'].str.split(' до ', expand=True)

    # удаляем столбец
    df = df.drop(columns=["line2"])

    # поменяем местами столбцы
    df = df[["id", "name", "city", "address", "lat", "lon", "code", "chat", "timezone", "workTimeStart", "workTimeEnd"]]

    # Сохранение DataFrame в JSON файл
    df.to_json("stores.json", orient="records", force_ascii=False, indent=4)

    print('Данные обработаны и сохранены')

    return df

# Для выполнения из терминала
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Использование: python processing.py https://www.parfum-lider.ru/upload/bot/map.json")
    else:
        path = sys.argv[1]
        processing_stores(path)
