import random
import time
from pyautogui import click, doubleClick, rightClick, leftClick, size as pyautogui_size
from logging import basicConfig, info, INFO
import os
import cv2 # Добавлено для find_image
import numpy as np # Добавлено для find_image

from modules import mousemover
from modules.find_image import find_image # Убедимся, что find_image импортирован

mover = mousemover.MouseMover()

# Создаем директорию для логов относительно текущей директории
LOGS_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE = "logs.log"
LOGS_PATH = os.path.join(LOGS_DIR, LOG_FILE)

# Create the log directory if it doesn't exist
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Set up logging configuration
basicConfig(level=INFO,
            filename=LOGS_PATH,
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s")

# Получаем размер основного экрана один раз при импорте модуля
try:
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui_size()
    DEFAULT_REGION = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
except Exception as e:
    # Запасной вариант на случай ошибки pyautogui
    print(f"Warning: Could not get screen size using pyautogui. Using default 1920x1080. Error: {e}")
    DEFAULT_REGION = (0, 0, 1920, 1080)


def hover(image: str, region: tuple = None, duration: float = 0.25, acc: float = 0.8):
    """Наводит курсор на центр найденного изображения."""
    if region is None:
        region = DEFAULT_REGION
    coords = find_image(image, region, acc=acc)
    if not coords:
        info(f"Hover failed: image '{image}' not found in region {region}.")
        return # Ничего не делаем, если изображение не найдено
    x1, y1, x2, y2 = coords
    duration = duration * random.randint(80, 120) / 100
    mover.move_to((x1 + x2) / 2, (y1 + y2) / 2, duration)

def lclick_on_image(image: str, region: tuple = None, duration: float = 0.25, acc: float = 0.8):
    """Наводит курсор и кликает левой кнопкой мыши на центр найденного изображения."""
    if region is None:
        region = DEFAULT_REGION
    coords = find_image(image, region, acc=acc)
    if not coords:
        info(f"Left click failed: image '{image}' not found in region {region}.")
        return # Ничего не делаем, если изображение не найдено
    x1, y1, x2, y2 = coords
    duration = duration * random.randint(80, 120) / 100
    target_x = (x1 + x2) / 2
    target_y = (y1 + y2) / 2
    mover.move_to(target_x, target_y, duration)
    time.sleep(0.05 * random.uniform(0.8, 1.2)) # Небольшая случайная задержка перед кликом
    click()

    info(f"Clicked on {image} at ({int(target_x)}, {int(target_y)})")


def dclick_on_image(image: str, region: tuple = None, duration: float = 0.25, acc: float = 0.8):
    """Наводит курсор и делает двойной клик левой кнопкой мыши на центр найденного изображения."""
    if region is None:
        region = DEFAULT_REGION
    coords = find_image(image, region, acc=acc)
    if not coords:
        info(f"Double click failed: image '{image}' not found in region {region}.")
        return # Ничего не делаем, если изображение не найдено
    x1, y1, x2, y2 = coords
    duration = duration * random.randint(80, 120) / 100
    target_x = (x1 + x2) / 2
    target_y = (y1 + y2) / 2
    mover.move_to(target_x, target_y, duration)
    time.sleep(0.05 * random.uniform(0.8, 1.2)) # Небольшая случайная задержка перед кликом
    doubleClick()

    info(f"Double clicked on {image} at ({int(target_x)}, {int(target_y)})")



def rclick_on_image(image: str, region: tuple = None, duration: float = 0.25, acc: float = 0.8):
    """Наводит курсор и кликает правой кнопкой мыши на центр найденного изображения."""
    if region is None:
        region = DEFAULT_REGION
    coords = find_image(image, region, acc=acc)
    if not coords:
        info(f"Right click failed: image '{image}' not found in region {region}.")
        return # Ничего не делаем, если изображение не найдено
    x1, y1, x2, y2 = coords
    duration = duration * random.randint(80, 120) / 100
    target_x = (x1 + x2) / 2
    target_y = (y1 + y2) / 2
    mover.move_to(target_x, target_y, duration)
    time.sleep(0.05 * random.uniform(0.8, 1.2)) # Небольшая случайная задержка перед кликом
    rightClick()

    info(f"Right clicked on {image} at ({int(target_x)}, {int(target_y)})")

def lclick(x: int, y: int, duration: float = 0.25):
    """Перемещает курсор в указанные координаты и кликает левой кнопкой мыши."""
    duration = duration * random.randint(80, 120) / 100
    mover.move_to(x, y, duration)
    time.sleep(0.05 * random.uniform(0.8, 1.2)) # Небольшая случайная задержка перед кликом
    leftClick()
    # Не логгируем здесь, т.к. координаты могут быть неинформативны без контекста