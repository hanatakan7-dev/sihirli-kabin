from flask import Blueprint, Response, render_template
import cv2

from ai.pose_detector import detect_pose
from ai.body_measure import calculate_body
from ai.cloth_overlay import overlay_cloth

# BLUEPRINT
ai_bp = Blueprint("ai", __name__)

# CAMERA
camera = cv2.VideoCapture(0)

# ---------------------------------------------------
# CAMERA GENERATOR
# ---------------------------------------------------

def generate_frames():

    while True:

        success, frame = camera.read()

        if not success:
            break

        temp_input = "static/results/live_input.jpg"

        temp_output = "static/results/live_output.jpg"

        cv2.imwrite(temp_input, frame)

        landmarks = detect_pose(
            temp_input,
            temp_output
        )

        processed = cv2.imread(temp_output)

        if processed is None:
            processed = frame

        ret, buffer = cv2.imencode(
            ".jpg",
            processed
        )

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )

# ---------------------------------------------------
# LIVE CAMERA
# ---------------------------------------------------

@ai_bp.route("/camera")
def camera_feed():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# ---------------------------------------------------
# AI CAMERA PAGE
# ---------------------------------------------------

@ai_bp.route("/ai-camera")
def ai_camera():

    return render_template(
        "ai_camera.html"
    )

# ---------------------------------------------------
# PROCESSING PAGE
# ---------------------------------------------------

@ai_bp.route("/processing")
def processing():

    return render_template(
        "processing.html"
    )

# ---------------------------------------------------
# BODY ANALYSIS
# ---------------------------------------------------

@ai_bp.route("/measurements")
def measurements():

    image_path = "static/scans/ON_POZ.jpg"

    output_path = "static/results/measure_result.jpg"

    landmarks = detect_pose(
        image_path,
        output_path
    )

    data = calculate_body(
        image_path,
        landmarks
    )

    return render_template(
        "measurements.html",
        data=data,
        result_image="/" + output_path
    )

# ---------------------------------------------------
# VIRTUAL FITTING PAGE
# ---------------------------------------------------

@ai_bp.route("/virtual-fitting")
def virtual_fitting():

    return render_template(
        "virtual_fitting.html"
    )

# ---------------------------------------------------
# AI RESULT
# ---------------------------------------------------

@ai_bp.route("/ai-result")
def ai_result():

    image_path = "static/scans/ON_POZ.jpg"

    cloth_path = "static/clothes/dress.png"

    output_path = "static/results/final_result.png"

    # POSE DETECT
    landmarks = detect_pose(
        image_path,
        output_path
    )

    # BODY ANALYSIS
    body_data = calculate_body(
        image_path,
        landmarks
    )

    # OVERLAY
    result = overlay_cloth(
        image_path,
        cloth_path,
        output_path,
        body_data
    )

    return render_template(
        "ai_result.html",
        result=result
    )