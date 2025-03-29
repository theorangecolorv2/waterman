from pyautogui import keyDown, keyUp, scroll, moveTo

from modules.click_on_image import lclick_on_image, lclick, hover
import time
import psutil
import subprocess
import pyautogui

from modules.find_image import exists, wait, find_image
from config import LAUNCHER_PATH, ACCOUNTS_FOLDER


def swap_accounts(launcher_path=None, current_account=None):
    """
    Функция для смены аккаунтов в EVE Online:
    1. Закрывает текущее окно игры
    2. Переводит фокус на лаунчер
    3. Выбирает следующий аккаунт (с прокруткой, если необходимо)
    4. Запускает игру с новым аккаунтом

    Args:
        launcher_path (str, optional): Путь к лаунчеру EVE Online
        current_account (int, optional): Индекс текущего аккаунта для выбора

    Returns:
        bool: True, если смена аккаунта прошла успешно, False в противном случае.
    """

    if not close_eve_game():
        print("Не удалось закрыть игру.")
        # Можно решить, продолжать ли, если игра не была найдена
        # return False # Раскомментировать, если нужно прервать выполнение

    # Если путь не указан, используется глобальная переменная
    if launcher_path is None:
        launcher_path = LAUNCHER_PATH

    if not focus_launcher(launcher_path):
        print("Не удалось сфокусироваться на лаунчере.")
        return False

    if not select_next_account(current_account):
        print(f"Не удалось выбрать аккаунт {current_account}.")
        return False

    launch_game()

    print("Аккаунт успешно сменен!")
    return True


def close_eve_game():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'exefile.exe' in proc.info['name'].lower():
            print(f"Закрываю процесс EVE: {proc.info['name']}")
            proc.kill()
            time.sleep(2)
            return True

    print("Не найден запущенный процесс EVE Online")
    return False


def focus_launcher(launcher_path=None):
    launcher_found = False

    # Если путь не указан, используется глобальная переменная
    if launcher_path is None:
        launcher_path = LAUNCHER_PATH

    for proc in psutil.process_iter(['pid', 'name']):
        if 'eve online' in proc.info['name'].lower():
            print("Лаунчер EVE уже запущен, переключаюсь на него")
            # Используем pyautogui для поиска окна лаунчера по изображению
            if exists("./assets/launcher_icon.png"):
                launcher_found = True
                lclick_on_image("./assets/launcher_icon.png")

    if not launcher_found:
        if launcher_path:
            print(f"Запускаю лаунчер EVE по пути: {launcher_path}")
            subprocess.Popen(launcher_path)
            time.sleep(5)
        else:
            print("Не указан путь к лаунчеру EVE")
            return False

    return True


def select_next_account(current_account=1):
    """
    Выбирает указанный аккаунт в лаунчере, прокручивая список при необходимости.

    Args:
        current_account (int): Индекс аккаунта для выбора (начиная с 1).

    Returns:
        bool: True, если аккаунт успешно выбран, False в противном случае.
    """
    time.sleep(2)

    print(f"Выбираю аккаунт {current_account}")
    account_path = f"{ACCOUNTS_FOLDER}/account_{current_account}.png"
    scroll_target_image = "./assets/for_scroll.png" # Изображение для наведения перед прокруткой

    print(f"Ищу изображение: {account_path}")

    scroll_attempts = 0
    max_scroll_attempts = 10 # Максимальное количество попыток прокрутки

    # Проверяем, виден ли аккаунт сразу
    while not exists(account_path) and scroll_attempts < max_scroll_attempts:
        print(f"Аккаунт {current_account} не найден. Пытаюсь прокрутить вниз (попытка {scroll_attempts + 1}/{max_scroll_attempts}).")

        # Наводим курсор на точку ниже scroll_target_image перед прокруткой
        try:
            scroll_target_coords = find_image(scroll_target_image)
            if scroll_target_coords:
                # Вычисляем центр изображения
                center_x = (scroll_target_coords[0] + scroll_target_coords[2]) / 2
                center_y = (scroll_target_coords[1] + scroll_target_coords[3]) / 2
                # Вычисляем точку на 80 пикселей ниже центра
                hover_x = center_x
                hover_y = center_y + 80
                print(f"Навожу курсор на ({hover_x}, {hover_y}) перед прокруткой.")
                moveTo(hover_x, hover_y, duration=0.1) # Используем moveTo
            else:
                 print(f"Не найдено изображение '{scroll_target_image}' для наведения курсора перед прокруткой.")
                 # Можно добавить запасной вариант или просто прокрутить без наведения
                 # Например, можно попробовать навестись на первый аккаунт, как было раньше
                 # first_account_path = f"{ACCOUNTS_FOLDER}/account_1.png"
                 # if exists(first_account_path):
                 #     hover(first_account_path, duration=0.1)

            time.sleep(0.2) # Небольшая пауза после наведения
            pyautogui.scroll(-150) # Прокручиваем вниз (значение можно подобрать)
            scroll_attempts += 1
            time.sleep(0.5) # Пауза после прокрутки для обновления интерфейса
        except Exception as e:
            print(f"Ошибка при поиске изображения, наведении или прокрутке: {e}")
            # Если произошла ошибка, можно попробовать прокрутить без наведения
            pyautogui.scroll(-150)
            scroll_attempts += 1
            time.sleep(0.5)

    # Финальная проверка после цикла прокрутки
    if exists(account_path):
        print(f"Аккаунт {current_account} найден. Кликаю.")
        lclick_on_image(account_path)
        return True
    else:
        print(f"Не удалось найти аккаунт {current_account} после {max_scroll_attempts} попыток прокрутки.")
        return False


def launch_game():
    if exists("./assets/update.png"):
        print("Ждем обновление")
        wait("./assets/play_button.png", duration=90)
    lclick_on_image("./assets/play_button.png")
    time.sleep(4)
    wait("./assets/nes.png", duration=40)
    time.sleep(3)
    _c = find_image("./assets/nes.png")
    print(_c)
    lclick((_c[0] + _c[2])/2 - 430, (_c[1] + _c[3])/2 - 340)
    time.sleep(10)
    keyDown("ctrl")
    time.sleep(0.1)
    keyDown("shift")
    time.sleep(0.1)
    keyDown("f9")
    time.sleep(0.1)
    keyUp("ctrl")
    keyUp("shift")
    keyUp("f9")
    
    # Проверяем оба изображения сразу, а не только ждем первое
    discovery_found = False
    time.sleep(7)
    # Проверяем наличие discovery.png
    if exists("./assets/discovery.png"):
        print("d1")
        lclick_on_image("./assets/discovery.png")
        discovery_found = True
    
    # Если discovery.png не найден, проверяем discovery2.png
    if not discovery_found and exists("./assets/discovery2.png"):
        print("d2")
        lclick_on_image("./assets/discovery2.png")
        discovery_found = True

    if not discovery_found and exists("./assets/d3.png"):
        print('d3')
        lclick_on_image("./assets/d3.png")
        discovery_found = True
        
    # Если ни один из вариантов не найден, пробуем подождать discovery2.png
    if not discovery_found:
        print("Ожидание discovery2.png...")
        if wait("./assets/discovery2.png", duration=7):
            print("d2 после ожидания")
            lclick_on_image("./assets/discovery2.png")
    
    time.sleep(1)

