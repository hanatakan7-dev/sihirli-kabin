import cv2
import mediapipe as mp

# MediaPipe
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=True,
    min_detection_confidence=0.5
)


def detect_pose(image_path, output_path):
    """
    İnsan vücudunu algılar.
    Landmark noktalarını çizer.
    Landmark listesini döndürür.
    """

    image = cv2.imread(image_path)

    if image is None:
        print("Görsel yüklenemedi:", image_path)
        return []

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    results = pose.process(rgb)

    landmarks_data = []

    if results.pose_landmarks:

        mp_draw.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        height, width, _ = image.shape

        for idx, lm in enumerate(
            results.pose_landmarks.landmark
        ):

            cx = int(lm.x * width)
            cy = int(lm.y * height)

            landmarks_data.append({
                "id": idx,
                "x": cx,
                "y": cy
            })

            cv2.circle(
                image,
                (cx, cy),
                4,
                (0, 255, 0),
                -1
            )

            cv2.putText(
                image,
                str(idx),
                (cx + 5, cy - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3,
                (255, 255, 255),
                1
            )

    else:
        print("Vücut algılanamadı.")

    cv2.imwrite(
        output_path,
        image
    )

    return landmarks_data