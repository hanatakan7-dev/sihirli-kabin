import cv2
import numpy as np


def create_body_mask(image_path):
    """
    Basit insan maskesi oluşturur.
    """

    image = cv2.imread(image_path)

    if image is None:
        return None

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    _, mask = cv2.threshold(
        gray,
        15,
        255,
        cv2.THRESH_BINARY
    )

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    mask = cv2.GaussianBlur(
        mask,
        (5, 5),
        0
    )

    mask = mask > 0

    return mask