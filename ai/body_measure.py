import cv2
import math


def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


def basic_estimation(frame_path):

    image = cv2.imread(frame_path)

    if image is None:
        return None

    height, width, _ = image.shape

    shoulder_width = int(width * 0.28)
    body_height = int(height * 0.72)
    waist_width = int(width * 0.22)

    size = "M"

    if shoulder_width < 180:
        size = "S"
    elif shoulder_width > 260:
        size = "L"

    return {

        "method": "basic_estimation",

        "shoulder_width": shoulder_width,

        "waist_width": waist_width,

        "body_height": body_height,

        "size": size
    }


def ai_measurement(pose_data):

    if not pose_data:
        return None

    left_shoulder = pose_data.get(
        "left_shoulder"
    )

    right_shoulder = pose_data.get(
        "right_shoulder"
    )

    left_hip = pose_data.get(
        "left_hip"
    )

    right_hip = pose_data.get(
        "right_hip"
    )

    left_ankle = pose_data.get(
        "left_ankle"
    )

    right_ankle = pose_data.get(
        "right_ankle"
    )

    nose = pose_data.get(
        "nose"
    )

    if (
        left_shoulder is None or
        right_shoulder is None or
        left_hip is None or
        right_hip is None or
        left_ankle is None or
        right_ankle is None or
        nose is None
    ):
        return None

    shoulder_width = distance(
        left_shoulder,
        right_shoulder
    )

    hip_width = distance(
        left_hip,
        right_hip
    )

    waist_width = hip_width * 0.85

    ankle_y = (
        left_ankle[1] +
        right_ankle[1]
    ) / 2

    body_height = ankle_y - nose[1]

    waist_center_x = (
        left_hip[0] +
        right_hip[0]
    ) / 2

    waist_center_y = (
        left_hip[1] +
        right_hip[1]
    ) / 2

    body_ratio = shoulder_width / max(
        hip_width,
        1
    )

    size = "M"

    if shoulder_width < 120:
        size = "S"

    elif shoulder_width > 220:
        size = "L"

    return {

        "method": "ai_measurement",

        "shoulder_width": round(
            shoulder_width,
            2
        ),

        "hip_width": round(
            hip_width,
            2
        ),

        "waist_width": round(
            waist_width,
            2
        ),

        "body_height": round(
            body_height,
            2
        ),

        "body_ratio": round(
            body_ratio,
            2
        ),

        "waist_center": (
            int(waist_center_x),
            int(waist_center_y)
        ),

        "size": size
    }


def calculate_body(
    frame_path,
    pose_data
):

    if pose_data:

        ai_data = ai_measurement(
            pose_data
        )

        if ai_data:
            return ai_data

    return basic_estimation(
        frame_path
    )