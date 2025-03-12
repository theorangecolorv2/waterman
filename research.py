import time
from datetime import datetime

from modules.click_on_image import lclick, lclick_on_image
from modules.find_image import find_image, make_screenshot, make_screenshot_part
from inference import analyze_image


time.sleep(1)

_c = find_image("./assets/demarcate.png")
corner = [((_c[0] + _c[2]) / 2) - 1392, ((_c[1] + _c[3]) / 2) + 20]
region = (int(corner[0]), int(corner[1]), 662, 662)

working = True

while working:
    #current_img = "./assets/inter.png"
    current_img = make_screenshot_part(region, image_path="./assets/662x662.png")
    analyze_image(current_img, corner)
    time.sleep(0.5)
    lclick_on_image("./assets/submit.png")
    time.sleep(0.3)
    lclick_on_image("./assets/continue.png")
    time.sleep(0.3)
    lclick_on_image("./assets/continue.png")
    time.sleep(1)





