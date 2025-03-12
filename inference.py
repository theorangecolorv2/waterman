import time
import os
import cv2
import numpy as np
import torch
import random
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from modules.click_on_image import lclick


def humanize_points(box, img_size=(662, 662), max_deviation=11):
    """
    Создает слегка неровные точки для прямоугольника, имитируя человеческие клики
    
    Args:
        box: Координаты прямоугольника [x1, y1, x2, y2]
        img_size: Размер изображения (ширина, высота)
        max_deviation: Максимальное отклонение в пикселях
    
    Returns:
        Список точек для клика с небольшими отклонениями
    """
    x1, y1, x2, y2 = map(int, box)  # Гарантируем, что исходные координаты целые
    
    # Создаем базовые точки прямоугольника
    base_points = [
        (x1, y1),  # верхний левый
        (x2, y1),  # верхний правый
        (x2, y2),  # нижний правый
        (x1, y2),  # нижний левый
        (x1, y1)   # снова верхний левый для замыкания
    ]
    
    humanized_points = []
    
    # Добавляем случайные отклонения к каждой точке, но сохраняем общую форму прямоугольника
    for i, (x, y) in enumerate(base_points):
        # Не добавляем отклонение к последней точке (она должна совпадать с первой)
        if i == 4:
            humanized_points.append(humanized_points[0])  # Используем точно первую точку для замыкания
            continue
            
        # Определяем допустимые диапазоны отклонений, чтобы не выйти за границы
        x_min_dev = max(-max_deviation, -x)
        x_max_dev = min(max_deviation, img_size[0] - x)
        y_min_dev = max(-max_deviation, -y)
        y_max_dev = min(max_deviation, img_size[1] - y)
        
        # Для сохранения прямоугольной формы ограничиваем отклонения
        # Углы могут двигаться в обоих направлениях, но с меньшей амплитудой
        if i == 0:  # верхний левый - может двигаться немного вниз и вправо
            x_dev = random.uniform(0, min(max_deviation/2, x_max_dev))
            y_dev = random.uniform(0, min(max_deviation/2, y_max_dev))
        elif i == 1:  # верхний правый - может двигаться немного вниз и влево
            x_dev = random.uniform(max(-max_deviation/2, x_min_dev), 0)
            y_dev = random.uniform(0, min(max_deviation/2, y_max_dev))
        elif i == 2:  # нижний правый - может двигаться немного вверх и влево
            x_dev = random.uniform(max(-max_deviation/2, x_min_dev), 0)
            y_dev = random.uniform(max(-max_deviation/2, y_min_dev), 0)
        elif i == 3:  # нижний левый - может двигаться немного вверх и вправо
            x_dev = random.uniform(0, min(max_deviation/2, x_max_dev))
            y_dev = random.uniform(max(-max_deviation/2, y_min_dev), 0)
        
        # Добавляем точку с отклонением, гарантируя целочисленные координаты
        humanized_points.append((int(x + x_dev), int(y + y_dev)))
    
    return humanized_points


def click_rectangle(box, corner, delay=0.1, humanize=True, img_size=(662, 662)):
    """
    Кликает по прямоугольнику, создавая 'человеческие' клики с небольшими отклонениями
    
    Args:
        box: Координаты прямоугольника [x1, y1, x2, y2]
        corner: Координаты угла экрана для позиционирования
        delay: Задержка между кликами
        humanize: Если True, клики будут имитировать человеческие
        img_size: Размер изображения (ширина, высота)
    """
    if humanize:
        points = humanize_points(box, img_size)
        
        # Добавляем случайные задержки для большей реалистичности
        for i, (x, y) in enumerate(points):
            # Случайная дополнительная задержка между кликами
            human_delay = delay + random.uniform(-0.02, 0.05) if i > 0 else delay
            # Ограничиваем минимальную задержку
            human_delay = max(0.05, human_delay)
            
            lclick(int(x + corner[0]), int(y + corner[1]))
            time.sleep(human_delay)
    else:
        # Старый вариант с идеальными прямоугольниками
        x1, y1, x2, y2 = box
        points = [
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
            (x1, y1)
        ]

        for x, y in points:
            lclick(int(x + corner[0]), int(y + corner[1]))
            time.sleep(delay)


def calculate_iou(box1, box2):
    """Рассчитывает IoU (Intersection over Union) между двумя прямоугольниками"""
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Вычисляем координаты пересечения
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)
    
    # Проверяем, есть ли пересечение
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    # Площадь пересечения
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Площади прямоугольников
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    # IoU
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    
    return iou


def check_containment(box1, box2, threshold=0.8):
    """Проверяет, содержится ли один прямоугольник внутри другого более чем на threshold"""
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Вычисляем координаты пересечения
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)
    
    # Проверяем, есть ли пересечение
    if x_right < x_left or y_bottom < y_top:
        return False, None
    
    # Площадь пересечения
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Площади прямоугольников
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    # Проверяем, содержится ли один в другом
    ratio1 = intersection_area / float(box1_area) if box1_area > 0 else 0
    ratio2 = intersection_area / float(box2_area) if box2_area > 0 else 0
    
    if ratio1 > threshold:
        return True, 0  # box1 содержится в box2
    elif ratio2 > threshold:
        return True, 1  # box2 содержится в box1
    
    return False, None


def filter_contained_boxes(boxes, scores=None, threshold=0.8):
    """Фильтрует прямоугольники, удаляя те, которые содержатся в других"""
    if len(boxes) <= 1:
        return boxes, scores
    
    to_keep = [True] * len(boxes)
    
    for i in range(len(boxes)):
        if not to_keep[i]:
            continue
            
        for j in range(len(boxes)):
            if i == j or not to_keep[j]:
                continue
                
            is_contained, container_idx = check_containment(boxes[i], boxes[j], threshold)
            
            if is_contained:
                # Определяем, какой прямоугольник оставить
                if container_idx == 0:  # box_i содержится в box_j
                    # Если есть scores, выбираем по уверенности, иначе оставляем больший
                    if scores is not None and scores[i] > scores[j]:
                        to_keep[j] = False
                    else:
                        to_keep[i] = False
                else:  # box_j содержится в box_i
                    if scores is not None and scores[j] > scores[i]:
                        to_keep[i] = False
                    else:
                        to_keep[j] = False
    
    filtered_boxes = [box for idx, box in enumerate(boxes) if to_keep[idx]]
    filtered_scores = None
    if scores is not None:
        filtered_scores = [score for idx, score in enumerate(scores) if to_keep[idx]]
    
    return filtered_boxes, filtered_scores


def resolve_overlaps(boxes, scores=None):
    """Разрешает пересечения прямоугольников, удаляя прямоугольники с меньшей уверенностью"""
    if len(boxes) <= 1:
        return boxes, scores
    
    to_keep = [True] * len(boxes)
    
    for i in range(len(boxes)):
        if not to_keep[i]:
            continue
            
        for j in range(i+1, len(boxes)):
            if not to_keep[j]:
                continue
                
            iou = calculate_iou(boxes[i], boxes[j])
            
            if iou > 0:  # Если есть пересечение
                # Если есть scores, выбираем по уверенности, иначе оставляем первый
                if scores is not None:
                    if scores[i] >= scores[j]:
                        to_keep[j] = False
                    else:
                        to_keep[i] = False
                else:
                    # Если нет scores, оставляем бокс с большей площадью
                    area_i = (boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1])
                    area_j = (boxes[j][2] - boxes[j][0]) * (boxes[j][3] - boxes[j][1])
                    if area_i >= area_j:
                        to_keep[j] = False
                    else:
                        to_keep[i] = False
    
    filtered_boxes = [box for idx, box in enumerate(boxes) if to_keep[idx]]
    filtered_scores = None
    if scores is not None:
        filtered_scores = [score for idx, score in enumerate(scores) if to_keep[idx]]
    
    return filtered_boxes, filtered_scores


def analyze_image(image_path, corner):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.WEIGHTS = os.path.join("./weights", "model_final_rect.pth")
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.35  # порог уверенности
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.MODEL.MASK_ON = False
    predictor = DefaultPredictor(cfg)

    image = cv2.imread(image_path)
    if image is None:
        print(f"Error loading image: {image_path}")
        return

    # Определяем размер изображения для ограничений
    img_height, img_width = image.shape[:2]
    img_size = (img_width, img_height)
        
    outputs = predictor(image)
    instances = outputs["instances"].to("cpu")
    vis_image = image.copy()

    if hasattr(instances, "pred_boxes"):
        boxes = instances.pred_boxes.tensor.cpu().numpy()
        scores = instances.scores.cpu().numpy() if hasattr(instances, "scores") else None
        
        # Конвертируем боксы в формат [x1, y1, x2, y2] для удобства
        boxes_list = [box.tolist() for box in boxes]
        
        # Фильтруем вложенные прямоугольники
        filtered_boxes, filtered_scores = filter_contained_boxes(boxes_list, scores, threshold=0.8)
        
        # Разрешаем пересечения прямоугольников
        final_boxes, final_scores = resolve_overlaps(filtered_boxes, filtered_scores)
        
        # Отображаем и кликаем по результирующим прямоугольникам
        humanized_vis_img = vis_image.copy()
        
        for box in final_boxes:
            x1, y1, x2, y2 = map(int, box)
            
            # Рисуем идеальный прямоугольник для сравнения
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Рисуем гуманизированный прямоугольник
            humanized_points = humanize_points(box, img_size)
            for i in range(len(humanized_points) - 1):
                pt1 = tuple(map(int, humanized_points[i]))
                pt2 = tuple(map(int, humanized_points[i+1]))
                cv2.line(humanized_vis_img, pt1, pt2, (0, 0, 255), 2)
            
            print(f"Clicking rectangle: {x1},{y1} - {x2},{y2}")
            # Используем гуманизированные клики
            click_rectangle(box, corner, delay=0.1, humanize=True, img_size=img_size)

        # Показываем оба результата для сравнения
        combined_img = np.hstack((vis_image, humanized_vis_img))
        cv2.imshow("Results (Left: Original, Right: Humanized)", combined_img)
        cv2.waitKey(30000)
        cv2.destroyAllWindows()