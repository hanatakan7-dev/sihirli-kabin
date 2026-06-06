import cv2


class ScalingEngine:

    def __init__(self):
        pass

    def calculate_scale(
        self,
        cloth_image_path,
        body_data,
        cloth_type="top"
    ):

        cloth = cv2.imread(
            cloth_image_path,
            cv2.IMREAD_UNCHANGED
        )

        if cloth is None:
            return None

        cloth_height, cloth_width = cloth.shape[:2]

        if cloth_type == "pants":

            body_width = body_data.get(
                "hip_width",
                180
            )

            target_width = int(
                body_width * 1.8
            )

        else:

            body_width = body_data.get(
                "shoulder_width",
                200
            )

            target_width = int(
                body_width * 2.4
            )

        scale_ratio = (
            target_width /
            max(cloth_width, 1)
        )

        target_height = int(
            cloth_height *
            scale_ratio
        )

        return {

            "target_width": target_width,

            "target_height": target_height,

            "scale_ratio": round(
                scale_ratio,
                3
            )

        }

    def resize_cloth(
        self,
        cloth_image_path,
        scale_data
    ):

        cloth = cv2.imread(
            cloth_image_path,
            cv2.IMREAD_UNCHANGED
        )

        if cloth is None:
            return None

        resized = cv2.resize(

            cloth,

            (
                scale_data["target_width"],
                scale_data["target_height"]
            ),

            interpolation=cv2.INTER_AREA

        )

        return resized


def detect_cloth_type(
    cloth_path
):

    cloth_path = cloth_path.lower()

    if (
        "pant" in cloth_path
        or
        "jean" in cloth_path
        or
        "trouser" in cloth_path
    ):
        return "pants"

    return "top"


def calculate_cloth_size(
    cloth_image_path,
    body_data
):

    engine = ScalingEngine()

    cloth_type = detect_cloth_type(
        cloth_image_path
    )

    return engine.calculate_scale(
        cloth_image_path,
        body_data,
        cloth_type
    )


def resize_cloth_image(
    cloth_image_path,
    body_data
):

    engine = ScalingEngine()

    cloth_type = detect_cloth_type(
        cloth_image_path
    )

    scale_data = engine.calculate_scale(
        cloth_image_path,
        body_data,
        cloth_type
    )

    if not scale_data:
        return None

    return engine.resize_cloth(
        cloth_image_path,
        scale_data
    )