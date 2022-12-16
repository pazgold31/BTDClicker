import cv2
from PIL import Image

from common.utils.picture_processing.opencv_utils import convert_image_to_cv2


def get_inner_image_position(image: Image.Image, inner_image: Image.Image, threshold: float) -> Tuple[int, int]:
    large_image = convert_image_to_cv2(image=image)
    small_image = convert_image_to_cv2(image=inner_image)

    # noinspection PyUnresolvedReferences
    result = cv2.matchTemplate(large_image, small_image[..., :3], cv2.TM_SQDIFF_NORMED, mask=small_image[..., 3])

    # noinspection PyUnresolvedReferences
    mn, _, location, _ = cv2.minMaxLoc(result)

    if mn > threshold:
        raise ValueError

    location_x, location_y = location
    length, height = small_image.shape[:2]

    return (location_x * 2 + length) / 2, (location_y * 2 + height) / 2
