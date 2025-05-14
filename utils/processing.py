import pandas as pd
import sys


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

    # приведение форматов
    df['workTimeStart'] = pd.to_datetime(df['workTimeStart'], format='%H:%M').dt.strftime('%H:%M:%S')
    df['workTimeEnd'] = pd.to_datetime(df['workTimeEnd'], format='%H:%M').dt.strftime('%H:%M:%S')
    df['timezone'] = pd.to_timedelta(df['timezone'] + ':00').dt.components.apply(
        lambda x: f"{x.hours:02}:{x.minutes:02}:{x.seconds:02}", axis=1
    )

    # удаляем столбец
    df = df.drop(columns=["line2"])

    # поменяем местами столбцы
    df = df[["id", "name", "city", "address", "lat", "lon", "code", "chat", "workTimeStart", "workTimeEnd", "timezone"]]

    # Сохранение DataFrame в JSON файл
    df.to_json("stores.json", orient="records", force_ascii=False, indent=4)

    # Сохранение DataFrame в CSV файл
    df.to_csv("output.csv", index=False, encoding="utf-8")

    print('Данные обработаны и сохранены')

    return df


# Для выполнения из терминала
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python processing.py https://www.parfum-lider.ru/upload/bot/map.json")
    else:
        path = sys.argv[1]
        processing_stores(path)
