from cv2 import imread, COLOR_BGR2GRAY, matchTemplate, TM_CCOEFF_NORMED, imshow, waitKey, rectangle, \
    COLOR_BGR2HSV, boundingRect, inRange, countNonZero, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, imread, cvtColor, Canny, \
    findContours, drawContours, mean, contourArea, FILLED, \
    destroyAllWindows, minMaxLoc, imwrite
import numpy as np
import pyautogui
import os
from logging import basicConfig, info, INFO
import time



LOGS_DIR = os.path.join(os.path.abspath("C:\\Users\\theorr\\PycharmProjects\\evebot\\logs"), "logs")  # Adjusted to point directly to logs directory
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


def find_image(finding_element: str, region: tuple = (0, 0, 1920, 1920), duration: float = 1, acc: float = 0.8) -> list:
    coordinates = make_template(finding_element, region)
    info(f"cords of {finding_element} added") if coordinates else info(f"image {finding_element} not found")
    return coordinates


def make_template(finding_element: str, region: tuple = (0, 0, 1920, 1920), acc: float = 0.8) -> list:
    frame = make_screenshot()

    # unpack tuple
    region_x, region_y, region_width, region_height = region

    # get img, cut screen
    img = imread(frame)
    roi = img[region_y:region_y + region_height, region_x:region_x + region_width]

    # get part
    template = imread(finding_element)
    if template is None or roi is None:
        info(f"load error of '{finding_element}' roi is empty")
        return []

    # ch/b
    roi_gray = cvtColor(roi, COLOR_BGR2GRAY)
    template_gray = cvtColor(template, COLOR_BGR2GRAY)

    # find wh
    w, h = template_gray.shape[::-1]

    # match algo
    result = matchTemplate(roi_gray, template_gray, TM_CCOEFF_NORMED)

    # accuracy
    threshold = acc  # 0.8 default
    loc = np.where(result >= threshold)

    coordinates = []

    for pt in zip(*loc[::-1]):
        coordinates.append((pt[0], pt[1], pt[0] + w, pt[1] + h))

    if coordinates:
        max_index = np.argmax(result[loc])
        best_match = coordinates[max_index]
        return list(best_match)
    else:
        info(f'cant found image {finding_element}')
        return []


def make_screenshot() -> str:
    image_path = "./assets/eve_screen.png"

    directory = os.path.dirname(image_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    src = pyautogui.screenshot(image_path)
    src.save(image_path)
    info("make screenshot")
    return os.path.abspath(image_path)


def wait(finding_element: str, region: tuple = (0, 0, 1920, 1920), duration: float = 20, interval: float = 1,
         acc: float = 0.8):
    start_time = time.time()
    coordinates = make_template(finding_element, region, acc=acc)

    while not coordinates:
        if time.time() - start_time > duration:
            info("didnt wait " + finding_element)
            return False
        time.sleep(interval)
        coordinates = make_template(finding_element, region, acc=acc)

    return True


def exists(finding_element: str, region: tuple = (0, 0, 1920, 1920), acc: float = 0.8):
    coordinates = make_template(finding_element, region, acc=acc)
    if coordinates:
        info(finding_element + ": exists")
        return True
    else:
        info(finding_element + ": not exists")
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