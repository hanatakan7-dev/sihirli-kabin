import math

# -----------------------------------
# DISTANCE
# -----------------------------------

def distance(x1, y1, x2, y2):

    return math.sqrt(

        (x2 - x1) ** 2 +

        (y2 - y1) ** 2

    )

# -----------------------------------
# LIVE MEASURE
# -----------------------------------

def live_measure(landmarks, width, height):

    if not landmarks:
        return None

    try:

        # SHOULDERS

        left_shoulder = landmarks[11]

        right_shoulder = landmarks[12]

        # HIPS

        left_hip = landmarks[23]

        right_hip = landmarks[24]

        # -----------------------------------
        # PIXELS
        # -----------------------------------

        sx1 = int(left_shoulder.x * width)
        sy1 = int(left_shoulder.y * height)

        sx2 = int(right_shoulder.x * width)
        sy2 = int(right_shoulder.y * height)

        hx1 = int(left_hip.x * width)
        hy1 = int(left_hip.y * height)

        hx2 = int(right_hip.x * width)
        hy2 = int(right_hip.y * height)

        # -----------------------------------
        # DISTANCE
        # -----------------------------------

        shoulder_width = int(

            distance(
                sx1, sy1,
                sx2, sy2
            )

        )

        hip_width = int(

            distance(
                hx1, hy1,
                hx2, hy2
            )

        )

        # -----------------------------------
        # BODY RATIO
        # -----------------------------------

        body_ratio = round(

            shoulder_width /

            (hip_width + 0.1),

            2

        )

        # -----------------------------------
        # SIZE
        # -----------------------------------

        size = "M"

        if shoulder_width < 110:
            size = "S"

        elif shoulder_width > 210:
            size = "L"

        # -----------------------------------
        # CONFIDENCE
        # -----------------------------------

        confidence = min(

            99,

            int(body_ratio * 45)

        )

        return {

            "shoulder_width": shoulder_width,

            "hip_width": hip_width,

            "body_ratio": body_ratio,

            "size": size,

            "confidence": confidence

        }

    except:

        return None