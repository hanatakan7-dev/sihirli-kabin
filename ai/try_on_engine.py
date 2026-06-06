from ai.pose_detector import detect_pose
from ai.body_measure import calculate_body
from ai.cloth_overlay import overlay_cloth


class VirtualTryOnEngine:

    def __init__(self):
        pass

    def process(
        self,
        person_image,
        cloth_image,
        output_image
    ):

        try:

            # 1. Pose Detection
            landmark_preview = output_image.replace(
                ".png",
                "_pose.png"
            )

            landmarks = detect_pose(
                person_image,
                landmark_preview
            )

            if not landmarks:

                return {
                    "success": False,
                    "step": "pose_detection",
                    "message": "Vücut algılanamadı."
                }

            # 2. Body Measurement
            body_data = calculate_body(
                person_image,
                landmarks
            )

            if not body_data:

                return {
                    "success": False,
                    "step": "body_measurement",
                    "message": "Ölçüler hesaplanamadı."
                }

            # 3. Overlay Cloth
            result_path = overlay_cloth(
                person_image=person_image,
                cloth_image=cloth_image,
                output_path=output_image,
                body_data=body_data,
                landmarks=landmarks
            )

            if not result_path:

                return {
                    "success": False,
                    "step": "cloth_overlay",
                    "message": "Kıyafet yerleştirilemedi."
                }

            return {
                "success": True,
                "result_image": result_path,
                "body_data": body_data,
                "landmarks_count": len(landmarks)
            }

        except Exception as e:

            return {
                "success": False,
                "step": "system",
                "message": str(e)
            }


def run_virtual_tryon(
    person_image,
    cloth_image,
    output_image
):

    engine = VirtualTryOnEngine()

    return engine.process(
        person_image,
        cloth_image,
        output_image
    )