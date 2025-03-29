import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Расширенный набор точек (включая реальные и промежуточные)
x_levels = np.array([9.0, 14.5, 15.2, 20.9, 24.5, 45.1,
                     10, 12, 16, 18, 22, 26, 30, 35, 40, 43, 47])
y_level_growth = np.array([5.1, 4.4, 4.5, 3.6, 3.3, 3.3,
                            5.0, 4.8, 4.2, 4.0, 3.8, 3.6, 3.4, 3.2, 3.1, 3.0, 2.9])

# Функция аппроксимации
def growth_approximation(x, a, b, c):
    return a / (1 + np.exp(b * (x - c)))

# Подбор параметров
popt, _ = curve_fit(growth_approximation, x_levels, y_level_growth,
                    p0=[4.5, 0.1, 25], maxfev=10000)

# Визуализация
plt.figure(figsize=(10, 6))
plt.scatter(x_levels, y_level_growth, color='blue', label='Данные')
x_model = np.linspace(min(x_levels), max(x_levels), 200)
plt.plot(x_model, growth_approximation(x_model, *popt), color='red', label='Аппроксимация')
plt.title('Аппроксимация прироста уровня')
plt.xlabel('Начальный уровень')
plt.ylabel('Прирост уровня')
plt.legend()
plt.grid(True)
plt.show()

# Формула и параметры
a, b, c = popt
print(f"Формула прироста уровня:")
print(f"growth = {a:.2f} / (1 + exp({b:.3f} * (x - {c:.2f})))")

# Проверка прогнозов
print("\nПрогнозы прироста уровня:")
for level in [10, 20, 30, 40, 50]:
    print(f"Уровень {level}: прирост {growth_approximation(level, *popt):.2f}")