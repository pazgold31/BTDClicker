import threading
import time
from datetime import timedelta
from pathlib import Path
from queue import Queue
from typing import Tuple, Dict, List, Optional

import cv2
import numpy as np
import pyautogui
from PIL import Image
from ahk import AHK

from common.monkey_knowledge.knowledge_dataclasses import KnowledgeCategory, KnowledgeEntry
from common.monkey_knowledge.knowledge_wiki_crawler import download_knowledge_pictures
from common.user_files import get_knowledge_images_dir, get_files_dir
from common.utils.cashed_dataclasses.cashed_dataclasses_utils import load_cached_dataclass, save_dataclass_to_cache


class KnowledgeDirectories:
    PRIMARY = get_knowledge_images_dir(subdirectory="Primary Knowledge")
    MILITARY = get_knowledge_images_dir(subdirectory="Military Knowledge")
    MAGIC = get_knowledge_images_dir(subdirectory="Magic Knowledge")
    SUPPORT = get_knowledge_images_dir(subdirectory="Support Knowledge")
    HERO = get_knowledge_images_dir(subdirectory="Heroes Knowledge")
    POWERS = get_knowledge_images_dir(subdirectory="Powers Knowledge")


KNOWLEDGE_DIRECTORIES_ORDER = [
    KnowledgeDirectories.PRIMARY,
    KnowledgeDirectories.MILITARY,
    KnowledgeDirectories.MAGIC,
    KnowledgeDirectories.SUPPORT,
    KnowledgeDirectories.HERO,
    KnowledgeDirectories.POWERS
]

MONKEY_KNOWLEDGE_IMAGE = Image.open(str(get_knowledge_images_dir() / "Knowledge Icon.png"))
PRIMARY_KNOWLEDGE_ICON_IMAGE = Image.open(str(get_knowledge_images_dir() / "PrimaryIcon.png"))
NEXT_BUTTON_IMAGE = Image.open(str(get_knowledge_images_dir() / "NextButton.png"))

KNOWLEDGE_UPDATE_TIME = timedelta(days=14)

DEFAULT_KNOWLEDGE_THRESHOLD = 0.1
KNOWLEDGE_MENU_THRESHOLD = 0.15
NEXT_BUTTON_THRESHOLD = 0.01
PRIMARY_MENU_THRESHOLD = 0.05
DEFAULT_MOUTH_POSITION = (815, 105)


def get_knowledge_threshold(knowledge_name: str):
    # TODO: find a better way to do this.
    if "Sub Admiral" == knowledge_name:
        return 0.02
    else:
        return DEFAULT_KNOWLEDGE_THRESHOLD


def convert_image_to_cv2(image: Image.Image) -> np.ndarray:
    # noinspection PyTypeChecker
    cv_image = np.array(image)  # 'image' Color order: RGBA
    red = cv_image[:, :, 0].copy()  # Copy R from RGBA
    cv_image[:, :, 0] = cv_image[:, :, 2].copy()  # Copy B to first order. Color order: BGBA
    cv_image[:, :, 2] = red  # Copy R to the third order. Color order: BGRA
    return cv_image


def get_inner_image_position(image: Image.Image, inner_image: Image.Image, threshold: float) -> Tuple[int, int]:
    large_image = convert_image_to_cv2(image=image)
    small_image = convert_image_to_cv2(image=inner_image)

    result = cv2.matchTemplate(large_image, small_image[..., :3], cv2.TM_SQDIFF_NORMED, mask=small_image[..., 3])

    mn, _, location, _ = cv2.minMaxLoc(result)

    if mn > threshold:
        raise ValueError

    location_x, location_y = location
    length, height = small_image.shape[:2]

    return (location_x * 2 + length) / 2, (location_y * 2 + height) / 2


def click_image(ahk: AHK, image: Image.Image, threshold: float):
    screenshot = pyautogui.screenshot()
    pos = get_inner_image_position(image=screenshot,
                                   inner_image=image,
                                   threshold=threshold)

    ahk.mouse_position = (pos[0], pos[1])
    ahk.click()


def open_monkey_knowledge(ahk: AHK):
    click_image(ahk=ahk, image=MONKEY_KNOWLEDGE_IMAGE, threshold=KNOWLEDGE_MENU_THRESHOLD)


def open_primary_monkey_knowledge(ahk: AHK):
    click_image(ahk=ahk, image=PRIMARY_KNOWLEDGE_ICON_IMAGE, threshold=PRIMARY_MENU_THRESHOLD)


def get_knowledge_map(images_directory: Path, screenshot: Image.Image) -> Dict[str, bool]:
    output = {}
    for file_path in images_directory.glob("*.png"):
        knowledge_name = file_path.stem
        file_image = Image.open(str(file_path))
        try:
            get_inner_image_position(image=screenshot, inner_image=file_image,
                                     threshold=get_knowledge_threshold(knowledge_name=knowledge_name))
            output[knowledge_name] = True
        except ValueError:
            output[knowledge_name] = False

    return output


def scroll_down(ahk: AHK):
    ahk.send("{WheelDown}")


def get_category_knowledge(images_directory: Path, screenshots: List[Image.Image]) -> KnowledgeCategory:
    dicts = [get_knowledge_map(images_directory=images_directory, screenshot=i) for i in screenshots]
    combined_dict = {k: any(i[k] for i in dicts) for k in dicts[0].keys()}
    knowledge_entries = [KnowledgeEntry(name=k, purchased=v) for k, v in combined_dict.items()]
    return KnowledgeCategory(name=images_directory.stem, entries=knowledge_entries)


def get_category_screenshots(ahk) -> List[Image.Image]:
    output = [pyautogui.screenshot()]
    scroll_down(ahk=ahk)
    time.sleep(0.5)
    output.append(pyautogui.screenshot())

    return output


def click_next_button(ahk: AHK):
    click_image(ahk=ahk, image=NEXT_BUTTON_IMAGE, threshold=NEXT_BUTTON_THRESHOLD)


def move_mouse_from_button(ahk: AHK):
    ahk.mouse_position = DEFAULT_MOUTH_POSITION


SLEEP_INTERVAL = 0.8


def crawl_monkey_knowledge() -> List[KnowledgeCategory]:
    ahk = AHK()
    open_monkey_knowledge(ahk=ahk)
    time.sleep(SLEEP_INTERVAL)
    open_primary_monkey_knowledge(ahk=ahk)
    time.sleep(SLEEP_INTERVAL)
    threads = []
    output_queue = Queue()
    for images_directory in KNOWLEDGE_DIRECTORIES_ORDER:
        move_mouse_from_button(ahk=ahk)
        time.sleep(SLEEP_INTERVAL)
        category_screenshots = get_category_screenshots(ahk=ahk)

        def run_and_add_to_queue(category_images_directory: Path, screenshots: List[Image.Image]):
            output_queue.put(
                get_category_knowledge(images_directory=category_images_directory, screenshots=screenshots))

        threads.append(threading.Thread(target=run_and_add_to_queue, args=(images_directory, category_screenshots,)))
        click_next_button(ahk=ahk)
        time.sleep(SLEEP_INTERVAL)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    return list(output_queue.queue)


def update_monkey_knowledge_info():
    path = get_files_dir() / "monkey_knowledge.json"
    download_knowledge_pictures()
    info_data = crawl_monkey_knowledge()
    save_dataclass_to_cache(path=path, info_data=info_data)


def get_monkey_knowledge_info() -> Optional[List[KnowledgeCategory]]:
    path = get_files_dir() / "monkey_knowledge.json"
    try:
        return load_cached_dataclass(path=path, output_type=List[KnowledgeCategory], update_time=KNOWLEDGE_UPDATE_TIME)
    except FileNotFoundError:
        return None
