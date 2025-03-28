import random
import time
from pyautogui import click, doubleClick, rightClick, leftClick
from logging import basicConfig, info, INFO
import os

from modules import mousemover
from modules.find_image import find_image

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


def hover(image: str, region: tuple = (0, 0, 1920, 1920), duration: float = 0.25, acc: float = 0.8):
    x1, y1, x2, y2 = find_image(image, region, acc=acc)
    duration = duration * random.randint(80, 120) / 100
    mover.move_to((x1 + x2) / 2, (y1 + y2) / 2, duration)

def lclick_on_image(image: str, region: tuple = (0, 0, 1920, 1920), duration: float = 0.25, acc: float = 0.8):
    x1, y1, x2, y2 = find_image(image, region, acc=acc)
    duration = duration * random.randint(80, 120) / 100
    mover.move_to((x1 + x2) / 2, (y1 + y2) / 2, duration)
    time.sleep(0.05)
    click()

    info(f"click on {image}")


def dclick_on_image(image: str, region: tuple = (0, 0, 1920, 1920), duration: float = 0.25, acc: float = 0.8):
    x1, y1, x2, y2 = find_image(image, region, acc=acc)
    duration = duration * random.randint(80, 120) / 100
    mover.move_to((x1 + x2) / 2, (y1 + y2) / 2, duration)
    time.sleep(0.05)
    doubleClick()

    info(f"double click on {image}")



def rclick_on_image(image: str, region: tuple = (0,0,1920,1920), duration: float = 0.25, acc: float = 0.8):
    x1, y1, x2, y2 = find_image(image, region, acc=acc)
    duration = duration * random.randint(80, 120) / 100
    mover.move_to((x1 + x2) / 2, (y1 + y2) / 2, duration)
    time.sleep(0.05)
    rightClick()

    info(f"rclick click on {image}")

def lclick(x: int, y: int, duration: float = 0.25):
    duration = duration * random.randint(80, 120) / 100
    mover.move_to(x, y, duration)
    time.sleep(0.05)
    leftClick()