from datetime import datetime

from cv2 import imread, COLOR_BGR2GRAY, matchTemplate, TM_CCOEFF_NORMED, imshow, waitKey, rectangle, \
    COLOR_BGR2HSV, boundingRect, inRange, countNonZero, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, imread, cvtColor, Canny, \
    findContours, drawContours, mean, contourArea, FILLED, \
    destroyAllWindows, minMaxLoc, imwrite, COLOR_RGB2BGR
import numpy as np
import pyautogui
import os
from logging import basicConfig, info, INFO
import time


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
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
    DEFAULT_REGION = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
except Exception as e:
    # Запасной вариант на случай ошибки pyautogui
    print(f"Warning: Could not get screen size using pyautogui. Using default 1920x1080. Error: {e}")
    DEFAULT_REGION = (0, 0, 1920, 1080)


def find_image(finding_element: str, region: tuple = None, duration: float = 1, acc: float = 0.8) -> list:
    """
    Ищет изображение на экране в указанном регионе.

    Args:
        finding_element (str): Путь к файлу изображения для поиска.
        region (tuple, optional): Регион поиска (x, y, width, height).
                                  По умолчанию используется весь экран.
        duration (float, optional): Не используется в этой функции напрямую.
        acc (float, optional): Минимальная точность совпадения (от 0.0 до 1.0). По умолчанию 0.8.

    Returns:
        list: Список координат [x1, y1, x2, y2] найденного изображения или пустой список.
    """
    if region is None:
        region = DEFAULT_REGION
    coordinates = make_template(finding_element, region, acc=acc)
    # Удален print(coordinates), так как он может засорять лог
    info(f"cords of {finding_element} added") if coordinates else info(f"image {finding_element} not found")
    return coordinates


def make_template(finding_element: str, region: tuple = None, acc: float = 0.8) -> list:
    """
    Выполняет сопоставление шаблона на скриншоте указанного региона.

    Args:
        finding_element (str): Путь к файлу шаблона.
        region (tuple, optional): Регион поиска (x, y, width, height).
                                  По умолчанию используется весь экран.
        acc (float, optional): Порог точности совпадения.

    Returns:
        list: Координаты лучшего совпадения [x1, y1, x2, y2] или пустой список.
    """
    if region is None:
        region = DEFAULT_REGION

    # Создаем скриншот ТОЛЬКО нужного региона для оптимизации
    try:
        frame_pil = pyautogui.screenshot(region=region)
        if frame_pil is None:
             raise ValueError("pyautogui.screenshot returned None")
        # Конвертируем PIL Image (RGB) в OpenCV формат (BGR)
        frame = cvtColor(np.array(frame_pil), COLOR_RGB2BGR)
    except Exception as e:
        info(f"Error taking screenshot for region {region}: {e}")
        # Попробуем сделать скриншот всего экрана как запасной вариант
        try:
            frame_pil = pyautogui.screenshot()
            if frame_pil is None:
                 raise ValueError("Fallback pyautogui.screenshot returned None")
            # Конвертируем PIL Image (RGB) в OpenCV формат (BGR)
            frame = cvtColor(np.array(frame_pil), COLOR_RGB2BGR)
            # Обрежем его до нужного региона, если это возможно
            region_x, region_y, region_width, region_height = region
            img_height, img_width = frame.shape[:2]
            # Корректируем регион, если он выходит за пределы скриншота
            region_x = max(0, region_x)
            region_y = max(0, region_y)
            region_width = min(region_width, img_width - region_x)
            region_height = min(region_height, img_height - region_y)
            frame = frame[region_y:region_y + region_height, region_x:region_x + region_width]
        except Exception as e_fallback:
             info(f"Fallback screenshot also failed: {e_fallback}")
             return []


    # Загружаем шаблон
    template = imread(finding_element)

    if template is None:
        info(f"Load error: Could not read template image '{finding_element}'")
        return []
    if frame is None or frame.size == 0:
        info(f"Load error: Screenshot region is empty or could not be captured.")
        return []

    # Проверка размеров: шаблон не может быть больше изображения, на котором ищем
    template_h, template_w = template.shape[:2]
    frame_h, frame_w = frame.shape[:2]
    if template_h > frame_h or template_w > frame_w:
        info(f"Template '{finding_element}' ({template_w}x{template_h}) is larger than the search region ({frame_w}x{frame_h}).")
        return []

    # ch/b
    try:
        roi_gray = cvtColor(frame, COLOR_BGR2GRAY) # roi теперь это весь frame (регион)
        template_gray = cvtColor(template, COLOR_BGR2GRAY)
    except cv2.error as e:
        info(f"OpenCV error during color conversion for '{finding_element}': {e}")
        return []

    # find wh
    w, h = template_gray.shape[::-1]

    # match algo
    try:
        result = matchTemplate(roi_gray, template_gray, TM_CCOEFF_NORMED)
    except cv2.error as e:
        info(f"OpenCV error during matchTemplate for '{finding_element}': {e}")
        # Это может произойти, если шаблон или изображение имеют несовместимые типы/размеры после всех проверок
        return []


    # accuracy
    threshold = acc
    min_val, max_val, min_loc, max_loc = minMaxLoc(result) # Находим только лучшее совпадение

    coordinates = []
    if max_val >= threshold:
        # Координаты лучшего совпадения относительно региона
        match_x, match_y = max_loc
        # Рассчитываем абсолютные координаты на экране
        region_x, region_y, _, _ = region
        abs_x1 = region_x + match_x
        abs_y1 = region_y + match_y
        abs_x2 = abs_x1 + w
        abs_y2 = abs_y1 + h
        coordinates = [abs_x1, abs_y1, abs_x2, abs_y2]
        # info(f"Found {finding_element} at {coordinates} with confidence {max_val:.2f}") # Опционально для отладки
        return coordinates # Возвращаем только лучшее совпадение
    else:
        info(f'Cant find image {finding_element} with confidence >= {threshold} (max confidence: {max_val:.2f})')
        return []


def make_screenshot(image_path = "../assets/temp_screenshot.png") -> str:
    image_path = image_path
    directory = os.path.dirname(image_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    src = pyautogui.screenshot(image_path)
    src.save(image_path)
    src.save("../CHECK.png")
    info("make screenshot")
    return os.path.abspath(image_path)

def make_screenshot_part(region, image_path = "./assets/temp_screenshot.png"):
    image_path = image_path
    directory = os.path.dirname(image_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    src = pyautogui.screenshot(image_path, region=region)
    src.save(image_path)
    #src.save("./assets/scr/" + str(datetime.now())[17:].replace(".", "") + ".png")
    info("make screenshot")
    return os.path.abspath(image_path)


def wait(finding_element: str, region: tuple = None, duration: float = 20, interval: float = 1, acc: float = 0.8):
    """
    Ожидает появления изображения в указанном регионе.

    Args:
        finding_element (str): Путь к файлу изображения.
        region (tuple, optional): Регион поиска (x, y, width, height).
                                  По умолчанию используется весь экран.
        duration (float, optional): Максимальное время ожидания в секундах.
        interval (float, optional): Интервал между проверками в секундах.
        acc (float, optional): Минимальная точность совпадения.

    Returns:
        bool: True, если изображение найдено, False - если время ожидания истекло.
    """
    if region is None:
        region = DEFAULT_REGION
    start_time = time.time()
    # Первая попытка поиска без ожидания
    coordinates = make_template(finding_element, region, acc=acc)

    while not coordinates:
        if time.time() - start_time > duration:
            info(f"Timeout waiting for {finding_element} after {duration} seconds.")
            return False
        time.sleep(interval)
        coordinates = make_template(finding_element, region, acc=acc)

    info(f"Successfully found {finding_element} after waiting.")
    return True


def exists(finding_element: str, region: tuple = None, acc: float = 0.8):
    """
    Проверяет, существует ли изображение в указанном регионе.

    Args:
        finding_element (str): Путь к файлу изображения.
        region (tuple, optional): Регион поиска (x, y, width, height).
                                  По умолчанию используется весь экран.
        acc (float, optional): Минимальная точность совпадения.

    Returns:
        bool: True, если изображение найдено, False в противном случае.
    """
    if region is None:
        region = DEFAULT_REGION
    coordinates = make_template(finding_element, region, acc=acc)
    if coordinates:
        # info(finding_element + ": exists") # Можно раскомментировать для детального лога
        return True
    else:
        # info(finding_element + ": not exists") # Можно раскомментировать для детального лога
        return False


def find_yellow(image_path):
    # Загружаем изображение
    image = imread(image_path)
    # Преобразуем в HSV цветовое пространство
    hsv = cvtColor(image, COLOR_BGR2HSV)

    # Определяем диапазоны для красного и желтого цветов
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])

    # Находим красные области
    red_mask = inRange(hsv, lower_red, upper_red)
    red_contours, _ = findContours(red_mask, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)

    # Проверяем наличие желтых рамок рядом с красными областями
    for contour in red_contours:
        x, y, w, h = boundingRect(contour)
        # Проверяем область вокруг красного объекта
        radius = 40

        # Убедимся, что область не выходит за пределы изображения
        yellow_area = image[max(0, y - radius):min(image.shape[0], y + h + radius),
                      max(0, x - radius):min(image.shape[1], x + w + radius)]

        yellow_hsv = cvtColor(yellow_area, COLOR_BGR2HSV)
        yellow_mask = inRange(yellow_hsv, lower_yellow, upper_yellow)
        yellow_count = countNonZero(yellow_mask)

        if yellow_count > 0:
            print(f'Найдены желтые рамки рядом с красным объектом на координатах ({x}, {y})')
            return True
        else:
            print(f'Нет желтых рамок рядом с красным объектом на координатах ({x}, {y})')
            return False


def determine_border_color(image_path):
    # Загружаем изображение
    image = imread(image_path)

    # Преобразуем изображение в оттенки серого
    gray = cvtColor(image, COLOR_BGR2GRAY)

    # Применяем Canny для обнаружения границ
    edges = Canny(gray, 50, 150)

    # Находим контуры
    contours, _ = findContours(edges, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return "Контуры не найдены"

    # Предполагаем, что интересующий нас контур - это самый большой
    largest_contour = max(contours, key=contourArea)

    # Получаем маску для этого контура
    mask = np.zeros_like(gray)
    drawContours(mask, [largest_contour], -1, (255, 255, 255), thickness=FILLED)

    # Вычисляем цвет границ
    mean_val = mean(image, mask=mask)[:3]  # Средние значения BGR

    # Определяем цвет по средним значениям
    if mean_val[0] < 45 and mean_val[1] < 45 and mean_val[2] < 45:  # Темно-серый
        return 'grey'
    elif mean_val[0] > 55 and mean_val[1] > 55 and mean_val[2] > 55:  # Белый
        return 'white'
    else:
        return 'Цвет не распознан'


def crop_object_from_screenshot(template_path, output_path):
    # Создаем скриншот
    screenshot = pyautogui.screenshot()

    # Сохраняем скриншот во временный файл
    screenshot_path = 'temp_screenshot.png'
    screenshot.save(screenshot_path)

    # Загружаем шаблон и скриншот
    template = imread(template_path)
    image = imread(screenshot_path)

    # Получаем размеры шаблона
    h, w = template.shape[:2]

    # Выполняем шаблонное сопоставление
    result = matchTemplate(image, template, method=TM_CCOEFF_NORMED)

    # Находим лучшее совпадение
    min_val, max_val, min_loc, max_loc = minMaxLoc(result)

    # Устанавливаем порог для совпадения (можно настроить по необходимости)
    threshold = 0.8
    if max_val >= threshold:
        # Определяем координаты для обрезки
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        # Обрезаем изображение по найденным координатам
        cropped_image = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        # Сохраняем обрезанное изображение
        imwrite(output_path, cropped_image)

        #imshow('Обрезанное изображение', cropped_image)
        #waitKey(0)
        #destroyAllWindows()

        return os.path.abspath(output_path)  # Возвращаем абсолютный путь к сохраненному изображению
    else:
        return "Объект не найден"


def can_lock():
    img = crop_object_from_screenshot("../assets/lock.png", "../assets/lock.png")
    if determine_border_color(img) == "white":
        return True
    elif determine_border_color(img) == "grey":
        return False
    return "cannot find image to determine color"