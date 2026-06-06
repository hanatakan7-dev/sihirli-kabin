    import cv2
    import numpy as np

    from ai.body_segmentation import create_body_mask

    # -----------------------------------
    # LANDMARK IDS
    # -----------------------------------

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    # -----------------------------------
    # GET POINT
    # -----------------------------------

    def get_point(landmarks, point_id):

    for point in landmarks:

    if point["id"] == point_id:
    return point

    return None

    # -----------------------------------
    # OVERLAY CLOTH
    # -----------------------------------

    def overlay_cloth(

    person_image,
    cloth_image,
    output_path,
    body_data,
    landmarks

    ):

    # -----------------------------------
    # LOAD PERSON
    # -----------------------------------

    person = cv2.imread(

    person_image,

    cv2.IMREAD_UNCHANGED

    )

    # -----------------------------------
    # LOAD CLOTH
    # -----------------------------------

    cloth = cv2.imread(

    cloth_image,

    cv2.IMREAD_UNCHANGED

    )

    # -----------------------------------
    # CHECK
    # -----------------------------------

    if person is None or cloth is None:

    return False

    # -----------------------------------
    # CLOTH TYPE
    # -----------------------------------

    cloth_name = cloth_image.lower()

    is_pants = (

    "pant" in cloth_name

    or

    "jean" in cloth_name

    )

    # -----------------------------------
    # BODY MASK
    # -----------------------------------

    body_mask = create_body_mask(

    person_image

    )

    if body_mask is None:

    cv2.imwrite(output_path, person)

    return output_path

    # -----------------------------------
    # LANDMARKS
    # -----------------------------------

    left_shoulder = get_point(

    landmarks,

    LEFT_SHOULDER

    )

    right_shoulder = get_point(

    landmarks,

    RIGHT_SHOULDER

    )

    left_elbow = get_point(

    landmarks,

    LEFT_ELBOW

    )

    right_elbow = get_point(

    landmarks,

    RIGHT_ELBOW

    )

    left_hip = get_point(

    landmarks,

    LEFT_HIP

    )

    right_hip = get_point(

    landmarks,

    RIGHT_HIP

    )

    left_knee = get_point(

    landmarks,

    LEFT_KNEE

    )

    right_knee = get_point(

    landmarks,

    RIGHT_KNEE

    )

    # -----------------------------------
    # FALLBACK
    # -----------------------------------

    if not left_shoulder or not right_shoulder:

    cv2.imwrite(output_path, person)

    return output_path

    # -----------------------------------
    # SHOULDER WIDTH
    # -----------------------------------

    shoulder_width = abs(

    right_shoulder["x"]

    -

    left_shoulder["x"]

    )

    # -----------------------------------
    # SMART SCALE
    # -----------------------------------

    cloth_width = int(

    shoulder_width * 2.4

    )

    # -----------------------------------
    # PANTS MODE
    # -----------------------------------

    if is_pants and left_hip and right_hip:

    hip_width = abs(

    right_hip["x"]

    -

    left_hip["x"]

    )

    cloth_width = int(

    hip_width * 1.8

    )

    cloth_ratio = (

    cloth.shape[0]

    /

    cloth.shape[1]

    )

    cloth_height = int(

    cloth_width * cloth_ratio

    )

    # -----------------------------------
    # PANTS HEIGHT
    # -----------------------------------

    if is_pants:

    cloth_height = int(

    cloth_height * 1.35

    )

    # -----------------------------------
    # RESIZE
    # -----------------------------------

    cloth = cv2.resize(

    cloth,

    (cloth_width, cloth_height)

    )

    # -----------------------------------
    # DYNAMIC BODY FIT
    # -----------------------------------

    waist_size = body_data.get(
    "waist_width",
    body_data.get("waist", 85)
    )

    chest_size = body_data.get(
    "chest_width",
    body_data.get("chest", 95)
    )

    # -----------------------------------
    # WAIST FIT
    # -----------------------------------

    if waist_size < 75:

    middle_ratio = 0.68

    elif waist_size < 90:

    middle_ratio = 0.80

    elif waist_size < 105:

    middle_ratio = 0.90

    else:

    middle_ratio = 1.0

    # -----------------------------------       
    # CHEST FIT
    # -----------------------------------

    if chest_size > 110:

    top_ratio = 1.08

    elif chest_size > 95:

    top_ratio = 1.0

    else:

    top_ratio = 0.92

    # -----------------------------------
    # APPLY
    # -----------------------------------

    top_width = int(

    cloth_width * top_ratio

    )

    middle_width = int(

    cloth_width * middle_ratio

    )

    bottom_width = int(

    cloth_width * 0.92

    )

    # -----------------------------------
    # BODY SHAPE WARP
    # -----------------------------------

    src = np.float32([

    [0, 0],
    [cloth_width, 0],

    [0, cloth_height],
    [cloth_width, cloth_height]

    ])

    dst = np.float32([

    [
    (cloth_width - top_width) / 2,
    0
    ],

    [
    (cloth_width + top_width) / 2,
    0
    ],

    [
    (cloth_width - bottom_width) / 2,
    cloth_height
    ],

    [
    (cloth_width + bottom_width) / 2,
    cloth_height
    ]

    ])

    warp_matrix = cv2.getPerspectiveTransform(

    src,
    dst

    )

    cloth = cv2.warpPerspective(

    cloth,

    warp_matrix,

    (cloth_width, cloth_height),

    borderMode=cv2.BORDER_TRANSPARENT

    )

    # -----------------------------------
    # SHOULDER ANGLE
    # -----------------------------------

    delta_y = (

    right_shoulder["y"]

    -

    left_shoulder["y"]

    )

    delta_x = (

    right_shoulder["x"]

    -

    left_shoulder["x"]

    )

    angle = np.degrees(

    np.arctan2(

    delta_y,

    delta_x

    )

    )

    # -----------------------------------
    # LEFT ARM ANGLE
    # -----------------------------------

    left_arm_angle = 0

    if left_elbow:

    left_arm_angle = np.degrees(

    np.arctan2(

    left_elbow["y"] - left_shoulder["y"],

    left_elbow["x"] - left_shoulder["x"]

    )

    )

    # -----------------------------------
    # RIGHT ARM ANGLE
    # -----------------------------------

    right_arm_angle = 0

    if right_elbow:

    right_arm_angle = np.degrees(

    np.arctan2(

    right_elbow["y"] - right_shoulder["y"],

    right_elbow["x"] - right_shoulder["x"]

    )

    )

    # -----------------------------------
    # ROTATE CLOTH
    # -----------------------------------

    rotation_matrix = cv2.getRotationMatrix2D(

    (

    cloth_width // 2,

    cloth_height // 2

    ),

    angle,

    1.0

    )

    cloth = cv2.warpAffine(

    cloth,

    rotation_matrix,

    (cloth_width, cloth_height),

    flags=cv2.INTER_LINEAR,

    borderMode=cv2.BORDER_TRANSPARENT

    )

    # -----------------------------------
    # ARM BASED DEFORMATION
    # -----------------------------------

    arm_difference = abs(

    left_arm_angle

    -

    right_arm_angle

    )

    if arm_difference > 25:

    stretch = int(cloth_width * 0.08)

    deform_src = np.float32([

    [0, 0],
    [cloth_width, 0],

    [0, cloth_height],
    [cloth_width, cloth_height]

    ])

    deform_dst = np.float32([

    [0, 0],

    [cloth_width, stretch],

    [0, cloth_height],

    [cloth_width, cloth_height - stretch]

    ])

    deform_matrix = cv2.getPerspectiveTransform(

    deform_src,

    deform_dst

    )

    cloth = cv2.warpPerspective(

    cloth,

    deform_matrix,

    (cloth_width, cloth_height),

    borderMode=cv2.BORDER_TRANSPARENT

    )

    # -----------------------------------
    # CENTER POSITION
    # -----------------------------------

    center_x = int(

    (
    left_shoulder["x"]

    +

    right_shoulder["x"]

    ) / 2

    )

    top_y = int(

    (
    left_shoulder["y"]

    +

    right_shoulder["y"]

    ) / 2

    )

    # -----------------------------------
    # PANTS POSITION
    # -----------------------------------

    if is_pants and left_hip and right_hip:

    center_x = int(

    (
    left_hip["x"]

    +

    right_hip["x"]

    ) / 2

    )

    top_y = int(

    (
    left_hip["y"]

    +

    right_hip["y"]

    ) / 2

    )

    # -----------------------------------
    # OFFSETS
    # -----------------------------------

    x_offset = int(

    center_x

    -

    cloth_width / 2

    )

    y_offset = int(

    top_y

    -

    cloth_height * 0.18

    )

    # -----------------------------------
    # LIMITS
    # -----------------------------------

    if x_offset < 0:
    x_offset = 0

    if y_offset < 0:
    y_offset = 0

    # -----------------------------------
    # CHECK ALPHA
    # -----------------------------------

    if len(cloth.shape) < 3 or cloth.shape[2] < 4:

    cv2.imwrite(output_path, person)

    return output_path

    # -----------------------------------
    # IMAGE LIMITS
    # -----------------------------------

    y1 = y_offset
    y2 = y_offset + cloth_height

    x1 = x_offset
    x2 = x_offset + cloth_width

    # -----------------------------------
    # SCREEN LIMIT
    # -----------------------------------

    if y2 > person.shape[0]:
    y2 = person.shape[0]

    if x2 > person.shape[1]:
    x2 = person.shape[1]

    # -----------------------------------
    # REAL SIZE
    # -----------------------------------

    cloth = cloth[0:y2-y1, 0:x2-x1]

    # -----------------------------------
    # ALPHA
    # -----------------------------------

    alpha = cloth[:, :, 3] / 255.0

    alpha = np.dstack([alpha, alpha, alpha])

    # -----------------------------------
    # RGB
    # -----------------------------------

    cloth_rgb = cloth[:, :, :3]

    # -----------------------------------
    # PERSON AREA
    # -----------------------------------

    person_area = person[y1:y2, x1:x2]

    if person_area.shape[0] == 0 or person_area.shape[1] == 0:
    cv2.imwrite(output_path, person)
    return output_path

    # -----------------------------------
    # BLEND
    # -----------------------------------

    if cloth_rgb.shape[:2] != person_area.shape[:2]:
    cv2.imwrite(output_path, person)
    return output_path

    blended = (
    cloth_rgb * alpha
    +
    person_area * (1 - alpha)
    ).astype(np.uint8)

    # -----------------------------------
    # APPLY
    # -----------------------------------

    person[y1:y2, x1:x2] = blended

    # -----------------------------------
    # FOREGROUND PROTECTION
    # -----------------------------------

    mask_area = body_mask[y1:y2, x1:x2]

    foreground = person[y1:y2, x1:x2]

    person[y1:y2, x1:x2] = np.where(
    mask_area[:, :, np.newaxis],
    foreground,
    person[y1:y2, x1:x2]
    )

    # -----------------------------------
    # SAVE RESULT
    # -----------------------------------

    cv2.imwrite(
    output_path,
    person
    )

    return output_path