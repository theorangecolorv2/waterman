from pyautogui import keyDown, keyUp

from modules.click_on_image import lclick_on_image, lclick
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
    3. Выбирает следующий аккаунт
    4. Запускает игру с новым аккаунтом

    Args:
        launcher_path (str, optional): Путь к лаунчеру EVE Online
        current_account (int, optional): Индекс текущего аккаунта для выбора
    """

    close_eve_game()

    # Если путь не указан, используется глобальная переменная
    if launcher_path is None:
        launcher_path = LAUNCHER_PATH
    
    focus_launcher(launcher_path)

    select_next_account(current_account)

    launch_game()

    print("Аккаунт успешно сменен!")


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
    time.sleep(2)
    print(f"Выбираю аккаунт {current_account}")
    account_path = f"{ACCOUNTS_FOLDER}/account_{current_account}.png"
    print(f"Ищу изображение: {account_path}")
    lclick_on_image(account_path)

    return


def launch_game():
    lclick_on_image("./assets/play_button.png")
    time.sleep(4)
    wait("./assets/nes.png", duration=40)
    time.sleep(3)
    _c = find_image("./assets/nes.png")
    print(_c)
    lclick((_c[0] + _c[2])/2 - 430, (_c[1] + _c[3])/2 - 340)
    time.sleep(9)
    keyDown("ctrl")
    time.sleep(0.1)
    keyDown("shift")
    time.sleep(0.1)
    keyDown("f9")
    time.sleep(0.1)
    keyUp("ctrl")
    keyUp("shift")
    keyUp("f9")
    wait("./assets/discovery.png", duration=30)
    lclick_on_image("./assets/discovery.png")
    time.sleep(1)

