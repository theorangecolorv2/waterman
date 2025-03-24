import time
from datetime import datetime
import random
import os
import sys

from modules.click_on_image import lclick, lclick_on_image
from modules.find_image import find_image, make_screenshot, make_screenshot_part, exists
from inference import analyze_image
from config import LOOP_LIMIT, RANDOM_ACTIONS

#gam betta 33.7 lvl on the start 36.7 finish => 3 lvl per 100 ||
# || 36.7 start, 40 finish, 100 lim || 40 start w 97.4%. 45.1 end w 98.9% (bug dt??) >100
# persif 3.2 start, lim after 9, 4.7 end | 4.7 start, 7.9 end, 40 lim
#warden peterson 9 start, 14.1 end, 99 lim
#armenian 15.2 start w 86.9%, 19.7 finish w 90.1%
def account_process():
    time.sleep(1)

    # Проверяем существование директории assets
    if not os.path.exists("./assets"):
        os.makedirs("./assets")
        print("Создана директория assets")
    
    # Проверяем наличие необходимых изображений
    required_images = ["demarcate.png", "submit.png", "continue.png", "rewards.png", "close.png", "limit_day.png"]
    missing_images = []
    
    for img in required_images:
        if not os.path.exists(f"./assets/{img}"):
            missing_images.append(img)
    
    if missing_images:
        print(f"Отсутствуют следующие изображения в папке assets: {', '.join(missing_images)}")
        print("Пожалуйста, убедитесь, что все необходимые изображения находятся в папке assets")
        return "missing_assets"

    # Находим опорную точку на экране
    _c = find_image("./assets/demarcate.png")
    
    # Проверяем, что изображение найдено
    if not _c or len(_c) < 4:
        print("Не удалось найти опорную точку на экране (demarcate.png)")
        print("Убедитесь, что EVE Online запущена и видна соответствующая область экрана")
        return "reference_not_found"
    
    corner = [((_c[0] + _c[2]) / 2) - 1392, ((_c[1] + _c[3]) / 2) + 20]
    region = (int(corner[0]), int(corner[1]), 662, 662)
    failed, submitted, robust, considered, count = 0, 0, 0, 0, 0
    start_time = datetime.now()
    working = True

    try:
        while working:
            current_img = make_screenshot_part(region, image_path="./assets/662x662.png")
            analyze_image(current_img, corner)
            time.sleep(0.5)

            if not exists("./assets/submit.png"):
                print("Не найдена кнопка submit.png")
                time.sleep(2)
                continue
                
            lclick_on_image("./assets/submit.png")
            time.sleep(0.3)
            
            if count >= LOOP_LIMIT or exists("./assets/limit_day.png"):
                return "lim"

            #
            # if exists("./assets/flawed.png"): failed += 1
            # elif exists("./assets/robust.png"): robust += 1
            # elif exists("./assets/considered.png"): considered += 1
            # else: submitted += 1
            count += 1
            print(count)
            time.sleep(0.8 + random.random())

            if not exists("./assets/continue.png"):
                print("Не найдена кнопка continue.png")
                time.sleep(2)
                continue
                
            lclick_on_image("./assets/continue.png")
            time.sleep(0.4)
            lclick_on_image("./assets/continue.png")
            time.sleep(1.1 + random.random() + random.randint(0, 3))
            if RANDOM_ACTIONS and random.randint(0, 50) == 42:
                if exists("./assets/rewards.png"):
                    print("Выполняю рандомное действие: просмотр наград")
                    lclick_on_image("./assets/rewards.png")
                    time.sleep(random.random() + random.randint(3, 7))
                    if exists("./assets/close.png"):
                        lclick_on_image("./assets/close.png")
                    time.sleep(1)

            # if count % 5 == 0:
            #     print(start_time - datetime.now())
            #     start_time = datetime.now()
            # if count % 2 == 0:
            #     print("count: ", count)
            #     print("submitted(~80%): ", submitted)
            #     print("considered(50-70%): ", considered)
            #     print("robust(>90%): ", robust)
            #     print("failure:(<50%)", failed)
            #     print("total ~ ",(submitted * 0.87 + considered * 0.72 + robust * 0.95 + failed * 0.35)/count, "%")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return "error"

    return "completed"

if __name__ == "__main__":
    print(account_process())

