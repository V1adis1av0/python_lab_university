import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

# Чтение CSV файла
df = pd.read_csv("C:\\Users\\Vladislav\\Desktop\\Prog\\Learn\\py\\py\\test_git\\lab8\\cars.csv")

print("\nПервые 5 строк таблицы:")
print(df.head())
print("\nРазмер датасета:", df.shape)
print(f'    - Количетсво строк: {df.shape[0]}')
print(f'    - Количетсво столбцов: {df.shape[1]}')

print('\nИнформация о столбцах')
print(df.info())
print("\nСтатистическое описание числовых данных")
print(df.describe())
print('\nПроверка на пропущенные значения')
missing_values = df.isnull().sum()
print(missing_values[missing_values >= 0])
print("\n10 самых мощных автомобилей")
top10 = df.nlargest(10, 'Horsepower')[['Brand', 'Model', 'Horsepower']]
print(top10)

# Подготовка данных
X = df[["Horsepower"]]
Y = df["Price"]

# Создание модели
model = LinearRegression()

# Обучение модели
model.fit(X, Y)

# Предсказания
predictions = model.predict(X)

# График
plt.figure(figsize=(12, 7))

# Точки
plt.scatter(
    df["Horsepower"],
    df["Price"],
    s=80
)

# Линия регрессии
plt.plot(
    df["Horsepower"],
    predictions,
    linewidth=3
)

plt.title("Зависимость цены автомобиля от мощности", fontsize=16)

plt.xlabel("Мощность (л.с.)", fontsize=12)
plt.ylabel("Цена ($)", fontsize=12)

plt.grid(True)

plt.show()

# Прогнозирование
new_car = pd.DataFrame({
    "Horsepower": [300]
})

predicted_price = model.predict(new_car)

print("\nПрогноз цены автомобиля:")
print(f"Мощность: 300 л.с.")
print(f"Предполагаемая цена: {predicted_price[0]:.2f} $")



# Корреляционная тепловая карта
plt.figure(figsize=(10, 8))

# Выбираем только числовые колонки
numeric_df = df.select_dtypes(include=[np.number])
correlation = numeric_df.corr()

plt.subplot(2, 2, 1)
sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Корреляция между признаками", fontsize=12)

# 2×2 grid
plt.subplot(2, 2, 2)
plt.scatter(df["Weight"], df["Price"], alpha=0.7, s=60, edgecolors='black')
plt.xlabel("Масса (кг)", fontsize=10)
plt.ylabel("Цена ($)", fontsize=10)
plt.title("Цена от массы", fontsize=11)
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 3)
# Исключаем электромобили для наглядности зависимости
df_ice = df[df["Fuel_Consumption"] > 0]
plt.scatter(df_ice["Horsepower"], df_ice["Fuel_Consumption"], 
           alpha=0.7, s=60, c='orange', edgecolors='black')
plt.xlabel("Мощность (л.с.)", fontsize=10)
plt.ylabel("Расход (л/100км)", fontsize=10)
plt.title("Расход от мощности (ДВС)", fontsize=11)
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 4)
plt.scatter(df["Weight"], df["Fuel_Consumption"], 
           alpha=0.7, s=60, c='green', edgecolors='black')
plt.xlabel("Масса (кг)", fontsize=10)
plt.ylabel("Расход (л/100км)", fontsize=10)
plt.title("Расход от массы", fontsize=11)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


# Гистограммы распределения признаков
plt.figure(figsize=(14, 5))

plt.subplot(1, 3, 1)
plt.hist(df["Price"], bins=20, color='skyblue', edgecolor='black')
plt.xlabel("Цена ($)")
plt.title("Распределение цен")
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 2)
plt.hist(df["Horsepower"], bins=20, color='lightcoral', edgecolor='black')
plt.xlabel("Мощность (л.с.)")
plt.title("Распределение мощности")
plt.grid(True, alpha=0.3)

plt.subplot(1, 3, 3)
plt.hist(df["Weight"], bins=20, color='lightgreen', edgecolor='black')
plt.xlabel("Масса (кг)")
plt.title("Распределение массы")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


# Средние цены по брендам
plt.figure(figsize=(12, 6))
brand_avg = df.groupby("Brand")["Price"].mean().sort_values(ascending=False).head(10)
bars = plt.barh(brand_avg.index[::-1], brand_avg.values[::-1], 
                color=plt.cm.viridis(np.linspace(0.3, 0.9, 10)), edgecolor='black')
plt.xlabel("Средняя цена ($)")
plt.title("Топ-10 брендов по средней цене")
plt.grid(True, alpha=0.3, axis='x')

# Добавляем подписи значений на столбцы
for bar in bars:
    width = bar.get_width()
    plt.text(width + 5000, bar.get_y() + bar.get_height()/2, 
            f'${width:,.0f}', va='center', fontsize=9)

plt.tight_layout()
plt.show()

# Вывод метрик качества модели
r2 = r2_score(Y, predictions)
mae = mean_absolute_error(Y, predictions)
print(f"\nМетрики качества модели:")
print(f"   • R² (коэффициент детерминации): {r2:.4f}")
print(f"   • MAE (средняя абсолютная ошибка): ${mae:,.2f}")
print(f"   • Точность в %: {r2 * 100:.1f}% объяснённой дисперсии")

# Scatter с цветовым кодированием по расходу топлива
plt.figure(figsize=(10, 7))
scatter = plt.scatter(
    df["Horsepower"], 
    df["Price"],
    c=df["Fuel_Consumption"],
    cmap="RdYlGn_r",         
    s=100, 
    alpha=0.8,
    edgecolors='black'
)
plt.colorbar(scatter, label="Расход (л/100км)")
plt.xlabel("Мощность (л.с.)", fontsize=12)
plt.ylabel("Цена ($)", fontsize=12)
plt.title("Цена от мощности (цвет = расход топлива)", fontsize=14)
plt.grid(True, alpha=0.3)
plt.show()