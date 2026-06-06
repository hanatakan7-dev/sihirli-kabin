from flask import Blueprint
from flask import Response
from flask import render_template
from flask import jsonify
from flask import request
from flask import session

import cv2
import mediapipe as mp
import time
import os
import uuid

from ai.live_measure import live_measure
from ai.pose_detector import detect_pose
from ai.body_measure import calculate_body
from ai.cloth_overlay import overlay_cloth

camera_bp = Blueprint(
    "camera",
    __name__
)

# -----------------------------------
# MEDIAPIPE
# -----------------------------------

mp_pose = mp.solutions.pose

mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(

    static_image_mode=False,

    min_detection_confidence=0.5,

    min_tracking_confidence=0.5

)

# -----------------------------------
# CAMERA
# -----------------------------------

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)

camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

camera.set(cv2.CAP_PROP_FPS, 30)

# -----------------------------------
# GLOBAL FRAME
# -----------------------------------

latest_frame = None

# -----------------------------------
# FRAME GENERATOR
# -----------------------------------

def generate_frames():

    global latest_frame

    prev_time = 0

    while True:

        success, frame = camera.read()

        if not success:
            break

        latest_frame = frame.copy()

        # -----------------------------------
        # RESIZE
        # -----------------------------------

        frame = cv2.resize(
            frame,
            (960, 540)
        )

        # -----------------------------------
        # RGB
        # -----------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # -----------------------------------
        # POSE DETECTION
        # -----------------------------------

        results = pose.process(rgb)

        h, w, _ = frame.shape

        analysis = None

        # -----------------------------------
        # LANDMARKS
        # -----------------------------------

        if results.pose_landmarks:

            mp_draw.draw_landmarks(

                frame,

                results.pose_landmarks,

                mp_pose.POSE_CONNECTIONS,

                mp_draw.DrawingSpec(

                    color=(0,255,0),

                    thickness=2,

                    circle_radius=2

                ),

                mp_draw.DrawingSpec(

                    color=(255,255,255),

                    thickness=2

                )

            )

            landmarks = results.pose_landmarks.landmark

            # -----------------------------------
            # SHOULDER LINE
            # -----------------------------------

            left = landmarks[11]

            right = landmarks[12]

            x1 = int(left.x * w)
            y1 = int(left.y * h)

            x2 = int(right.x * w)
            y2 = int(right.y * h)

            cv2.line(

                frame,

                (x1, y1),

                (x2, y2),

                (255,0,255),

                4

            )

            # -----------------------------------
            # LIVE ANALYSIS
            # -----------------------------------

            analysis = live_measure(

                landmarks,

                w,

                h

            )

        # -----------------------------------
        # FPS
        # -----------------------------------

        current_time = time.time()

        fps = int(
            1 / (current_time - prev_time + 0.0001)
        )

        prev_time = current_time

        # -----------------------------------
        # HUD
        # -----------------------------------

        cv2.rectangle(

            frame,

            (20,20),

            (350,120),

            (20,20,20),

            -1

        )

        cv2.circle(

            frame,

            (45,50),

            8,

            (0,255,0),

            -1

        )

        cv2.putText(

            frame,

            "AI SMART MIRROR ACTIVE",

            (65,55),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255,255,255),

            2

        )

        cv2.putText(

            frame,

            f"FPS : {fps}",

            (40,90),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,255),

            2

        )

        # -----------------------------------
        # ANALYTICS PANEL
        # -----------------------------------

        if analysis:

            cv2.rectangle(

                frame,

                (20,140),

                (380,310),

                (20,20,20),

                -1

            )

            cv2.putText(

                frame,

                f"SIZE : {analysis['size']}",

                (40,180),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.9,

                (0,255,0),

                2

            )

            cv2.putText(

                frame,

                f"SHOULDER : {analysis['shoulder_width']}",

                (40,220),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255,255,255),

                2

            )

            cv2.putText(

                frame,

                f"BODY RATIO : {analysis['body_ratio']}",

                (40,260),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255,255,255),

                2

            )

            cv2.putText(

                frame,

                f"CONFIDENCE : %{analysis['confidence']}",

                (40,300),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0,255,255),

                2

            )

        # -----------------------------------
        # SCAN LINE
        # -----------------------------------

        scan_y = int(
            (time.time() * 150)
            %
            frame.shape[0]
        )

        cv2.line(

            frame,

            (0, scan_y),

            (frame.shape[1], scan_y),

            (255,0,255),

            2

        )

        # -----------------------------------
        # ENCODE
        # -----------------------------------

        ret, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        frame = buffer.tobytes()

        # -----------------------------------
        # STREAM
        # -----------------------------------

        yield (

            b'--frame\r\n'

            b'Content-Type: image/jpeg\r\n\r\n'

            + frame +

            b'\r\n'

        )

# -----------------------------------
# STREAM
# -----------------------------------

@camera_bp.route("/camera")
def camera_stream():

    return Response(

        generate_frames(),

        mimetype=
        "multipart/x-mixed-replace; boundary=frame"

    )

# -----------------------------------
# AI CAMERA PAGE
# -----------------------------------

@camera_bp.route("/ai-camera")
def ai_camera():

    return render_template(
        "ai_camera.html"
    )

# -----------------------------------
# CAPTURE + AI FITTING
# -----------------------------------

@camera_bp.route("/capture")
def capture():

    global latest_frame

    if latest_frame is None:

        return jsonify({

            "status": "error",

            "message": "Frame bulunamadı"

        })

    # -----------------------------------
    # FILE NAMES
    # -----------------------------------

    filename = f"{uuid.uuid4()}.jpg"

    save_path = os.path.join(

        "static/uploads",

        filename

    )

    result_output = os.path.join(

        "static/results",

        f"result_{filename}"

    )

    pose_output = os.path.join(

        "static/results",

        f"pose_{filename}"

    )

    # -----------------------------------
    # SAVE FRAME
    # -----------------------------------

    cv2.imwrite(

        save_path,

        latest_frame

    )

    # -----------------------------------
    # POSE DETECTION
    # -----------------------------------

    landmarks = detect_pose(

        save_path,

        pose_output

    )

    # -----------------------------------
    # BODY ANALYSIS
    # -----------------------------------

    body_data = calculate_body(

        save_path,

        landmarks

    )

    # -----------------------------------
    # SELECT CLOTH
    # -----------------------------------

    cloth_file = "tshirt.png"

    if session.get("try_product"):

        cloth_file = session[
            "try_product"
        ]["cloth_image"]

    cloth_path = os.path.join(

        "static/cloths",

        cloth_file

    )

    # -----------------------------------
    # SMART AI OVERLAY
    # -----------------------------------

    overlay_cloth(

        save_path,

        cloth_path,

        result_output,

        body_data,

        landmarks

    )

    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    return jsonify({

        "status": "success",

        "image": result_output

    })

# -----------------------------------
# RESULT PAGE
# -----------------------------------

@camera_bp.route("/result-page")
def result_page():

    image = request.args.get("img")

    return render_template(

        "result.html",

        result=image

    )