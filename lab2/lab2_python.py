# Открытие файла и чтение его по строкам
file = open('py\cars.txt', 'r')
content = file.readlines()

# список словарей
data = []

# Цикл для заполнения цикла словарей
for line in content:
    clean_line = line.strip()
    parts = clean_line.split(',')

    item = {
        "make": parts[0],
        "price": int(parts[1]),
        "count": int(parts[2])
    }

    data.append(item)

# Марка машины с максимальной общей стоимостью и сама стоимость этой машины
total_make = ''
max_cost = 0

# Цикл для вычисления максимальной общей стоимости машины
for i in range(len(data)):

    qwe = dict(data[i])
    current_cost = qwe['price'] * qwe['count']
    if current_cost > max_cost:
        total_make = qwe['make']
        max_cost = current_cost

#  Вывод результата
print("Марка машины с максимальной общей стоимостью:", total_make)

# Закрытие файла для чтения
file.close