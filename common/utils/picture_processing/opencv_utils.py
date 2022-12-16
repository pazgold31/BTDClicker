import numpy as np
from PIL import Image


def convert_image_to_cv2(image: Image.Image) -> np.ndarray:
    # noinspection PyTypeChecker
    cv_image = np.array(image)  # 'image' Color order: RGBA
    red = cv_image[:, :, 0].copy()  # Copy R from RGBA
    cv_image[:, :, 0] = cv_image[:, :, 2].copy()  # Copy B to first order. Color order: BGBA
    cv_image[:, :, 2] = red  # Copy R to the third order. Color order: BGRA
    return cv_image
