import cv2
import enum
import numpy as np
from typing import List, Tuple

# The original COCO skeleton type
COCO_MODEL = (
    ("NECK", "RIGHT_HIP"),
    ("RIGHT_HIP", "RIGHT_KNEE"),
    ("RIGHT_KNEE", "RIGHT_ANKLE"),
    ("NECK", "LEFT_HIP"),
    ("LEFT_HIP", "LEFT_KNEE"),
    ("LEFT_KNEE", "LEFT_ANKLE"),
    ("NECK", "RIGHT_SHOULDER"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
    ("RIGHT_ELBOW", "RIGHT_WRIST"),
    ("NECK", "LEFT_SHOULDER"),
    ("LEFT_SHOULDER", "LEFT_ELBOW"),
    ("LEFT_ELBOW", "LEFT_WRIST"),
    ("NECK", "NOSE"),
    ("NOSE", "RIGHT_EYE"),
    ("NOSE", "LEFT_EYE"),
    ("RIGHT_EYE", "RIGHT_EAR"),
    ("LEFT_EYE", "LEFT_EAR"),
)

# Skeleton with spine joint
COCO_MODEL_WITH_PELVIS = (
    ("NECK", "PELVIS"),
    ("NECK", "RIGHT_SHOULDER"),
    ("NECK", "LEFT_SHOULDER"),
    ("PELVIS", "RIGHT_HIP"),
    ("PELVIS", "LEFT_HIP"),
    ("NECK", "NOSE"),
    ("NOSE", "RIGHT_EYE"),
    ("NOSE", "LEFT_EYE"),
    ("RIGHT_EYE", "RIGHT_EAR"),
    ("LEFT_EYE", "LEFT_EAR"),
    ("RIGHT_HIP", "RIGHT_KNEE"),
    ("LEFT_HIP", "LEFT_KNEE"),
    ("RIGHT_KNEE", "RIGHT_ANKLE"),
    ("LEFT_KNEE", "LEFT_ANKLE"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
    ("LEFT_SHOULDER", "LEFT_ELBOW"),
    ("RIGHT_ELBOW", "RIGHT_WRIST"),
    ("LEFT_ELBOW", "LEFT_WRIST"),
)

# Coloring for each skeleton point
TYPE_TO_COLOR = {
    "UNKNOWN_SKELETON_POINT": (128, 128, 128),
    "NOSE": (179, 179, 179),
    "NECK": (179, 179, 179),
    "RIGHT_HIP": (0, 9, 96),
    "RIGHT_KNEE": (0, 15, 156),
    "RIGHT_ANKLE": (0, 25, 255),
    "LEFT_HIP": (96, 0, 0),
    "LEFT_KNEE": (176, 0, 0),
    "LEFT_ANKLE": (255, 0, 0),
    "RIGHT_SHOULDER": (96, 0, 96),
    "RIGHT_ELBOW": (176, 0, 176),
    "RIGHT_WRIST": (255, 0, 255),
    "LEFT_SHOULDER": (0, 96, 0),
    "LEFT_ELBOW": (0, 176, 0),
    "LEFT_WRIST": (0, 255, 0),
    "RIGHT_EYE": (0, 156, 156),
    "LEFT_EYE": (176, 176, 0),
    "RIGHT_EAR": (0, 255, 255),
    "LEFT_EAR": (255, 255, 0),
    "PELVIS": (0, 102, 255)
}

HEAD_KEYPOINTS = (
    'NOSE', 'RIGHT_EYE', 'LEFT_EYE', 'LEFT_EYE', 'RIGHT_EYE'
)

END_KEYPOINTS = (
    'LEFT_EAR', 'RIGHT_EAR', 'RIGHT_WRIST', 'LEFT_WRIST', 'RIGHT_ANKLE', 'LEFT_ANKLE'
)


class Position(enum.Enum):
    BOTTOM_RIGHT = 1
    BOTTOM_LEFT = 2
    TOP_RIGHT = 3
    TOP_LEFT = 4


def _generate_pelvis(points: List[dict]) -> List[dict]:
    new_points = points
    r_hip = [key_point for key_point in points if key_point['type'] == 'RIGHT_HIP']
    l_hip = [key_point for key_point in points if key_point['type'] == 'LEFT_HIP']

    if len(r_hip) > 0 and len(l_hip) > 0:
        pelvis_x = (r_hip[0]['x'] + l_hip[0]['x']) / 2
        pelvis_y = (r_hip[0]['y'] + l_hip[0]['y']) / 2
    elif len(l_hip) > 0:
        pelvis_x = l_hip[0]['x']
        pelvis_y = l_hip[0]['y']
    elif len(r_hip) > 0:
        pelvis_x = r_hip[0]['x']
        pelvis_y = r_hip[0]['y']
    else:
        return points

    d = {
        'x': pelvis_x,
        'y': pelvis_y,
        'type': 'PELVIS',
        'confidence': 0.9
    }
    new_points.append(dict(d))
    return new_points


def _draw_skeleton(
        canvas: np.array,
        points: List[dict],
        skip_unknown=True,
        model=COCO_MODEL_WITH_PELVIS,
        color_palette=TYPE_TO_COLOR,
        point_size=5,
        joint_width=3
) -> np.array:
    def skeleton_point_to_cv(pt):
        return (int(round(pt["x"])), int(round(pt["y"])))

    points = _generate_pelvis(points)
    # draw joints
    for edge in model:
        current_joint_width = joint_width
        u = edge[0]
        v = edge[1]
        u_list = [x for x in points if x["type"] == u]
        v_list = [x for x in points if x["type"] == v]
        if u_list and v_list:
            if u_list[0]['type'] in [] or v_list[0]['type'] in HEAD_KEYPOINTS:
                current_joint_width = int(np.ceil(current_joint_width * 0.6))
                current_joint_width = int(np.ceil(current_joint_width * 0.6))
            cv2.line(
                canvas,
                skeleton_point_to_cv(u_list[0]), skeleton_point_to_cv(v_list[0]),
                color_palette[v],
                current_joint_width,
                cv2.LINE_AA
            )

    # draw keypoints
    for pt in points:
        current_point_size = point_size
        if pt["type"] == "UNKNOWN_SKELETON_POINT" and skip_unknown:
            continue
        if pt['type'] in HEAD_KEYPOINTS:
            current_point_size = int(0.6 * current_point_size)

        if pt['type'] in END_KEYPOINTS:
            x, y = skeleton_point_to_cv(pt)
            pt1 = (x - current_point_size, y - current_point_size)
            pt2 = (x + current_point_size, y + current_point_size)
            cv2.rectangle(canvas, pt1, pt2, color=color_palette[pt["type"]], thickness=cv2.FILLED, lineType=cv2.LINE_AA)
        elif pt['type'] in ('PELVIS', 'NECK'):
            continue
        else:
            cv2.circle(
                canvas,
                skeleton_point_to_cv(pt),
                current_point_size,
                color_palette[pt["type"]],
                cv2.FILLED,
                cv2.LINE_AA
            )
    return canvas


def _get_bounding_box_thickness(bounding_box: dict, scale=1.0) -> float:
    smaller_side = min(bounding_box['width'], bounding_box['height']) * scale
    return (smaller_side * 0.5) / 48


def _draw_bounding_box(
        canvas: np.array,
        bounding_box: dict,
        color: tuple,
        scaling=1.0,
        f_border=0.0
) -> np.array:
    base_thickness = _get_bounding_box_thickness(bounding_box, scaling)
    thick = max(1, int(round(base_thickness * 6)))
    thin = max(1, int(round(base_thickness)))

    border = int(np.ceil(base_thickness * f_border))

    circle_radius = max(1, int(1.5 * thick))
    circle_center = max(1, 2 * thick)

    x0 = int(round(bounding_box['x'] * scaling))
    y0 = int(round(bounding_box['y'] * scaling))
    x1 = x0 + int(round(bounding_box['width'] * scaling)) - 1
    y1 = y0 + int(round(bounding_box['height'] * scaling)) - 1

    # Top and bottom thin boundaries
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 + 2 * circle_center, y0 - border),
        pt2=(x1 - 2 * circle_center, y0 + thin + border)
    )
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 + 2 * circle_center, y1 - thin - border),
        pt2=(x1 - 2 * circle_center, y1 + border)
    )

    # Thin side boundaries
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 - border, y0 + 2 * circle_center),
        pt2=(x0 + thin + border, y1 - 2 * circle_center)
    )
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x1 - thin - border, y0 + 2 * circle_center),
        pt2=(x1 + border, y1 - 2 * circle_center)
    )

    # Top-left thick boundaries
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 + circle_center, y0 - border),
        pt2=(x0 + 2 * circle_center + border, y0 + thick + border),
    )
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 - border, y0 + circle_center),
        pt2=(x0 + thick + border, y0 + 2 * circle_center + border)
    )

    # Top-right thick boundaries
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x1 - 2 * circle_center - border, y0 - border),
        pt2=(x1 - circle_center, y0 + thick + border)
    )
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x1 - thick - border, y0 + circle_center),
        pt2=(x1 + border, y0 + 2 * circle_center + border),
    )

    # Bottom-left thick boundaries
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 + circle_center, y1 - thick - border),
        pt2=(x0 + 2 * circle_center + border, y1 + border)
    )
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x0 - border, y1 - 2 * circle_center - border),
        pt2=(x0 + thick + border, y1 - circle_center)
    )

    # Bottom-right thick boundaries
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x1 - 2 * circle_center - border, y1 - thick - border),
        pt2=(x1 - circle_center, y1 + border)
    )
    cv2.rectangle(
        img=canvas, color=color, thickness=cv2.FILLED, lineType=cv2.LINE_AA,
        pt1=(x1 - thick - border, y1 - 2 * circle_center - border),
        pt2=(x1 + border, y1 - circle_center)
    )

    # Rounded corners TOP to Bottom, Left to Right
    cv2.ellipse(
        img=canvas,
        center=(x0 + circle_center, y0 + circle_center),
        axes=(circle_radius, circle_radius),
        angle=180.0, startAngle=0.0, endAngle=90.0,
        color=color, thickness=thick + 2 * border, lineType=cv2.LINE_AA)
    cv2.ellipse(
        img=canvas,
        center=(x1 - circle_center, y0 + circle_center),
        axes=(circle_radius, circle_radius),
        angle=270.0, startAngle=0.0, endAngle=90.0,
        color=color, thickness=thick + 2 * border, lineType=cv2.LINE_AA)
    cv2.ellipse(
        img=canvas,
        center=(x1 - circle_center, y1 - circle_center),
        axes=(circle_radius, circle_radius),
        angle=0.0, startAngle=0.0, endAngle=90.0,
        color=color, thickness=thick + 2 * border, lineType=cv2.LINE_AA)
    cv2.ellipse(
        img=canvas,
        center=(x0 + circle_center, y1 - circle_center),
        axes=(circle_radius, circle_radius),
        angle=90.0, startAngle=0.0, endAngle=90.0,
        color=color, thickness=thick + 2 * border, lineType=cv2.LINE_AA)

    return canvas


def _draw_3d_lines(canvas, center, directions):
    y_dir = (center[0] + directions[0][0], center[1] + directions[0][1])
    x_dir = (center[0] + directions[1][0], center[1] + directions[1][1])
    z_dir = (center[0] + directions[2][0], center[1] + directions[2][1])
    canvas = cv2.line(canvas, center, y_dir, (255, 0, 0), 2, cv2.LINE_AA)
    canvas = cv2.line(canvas, center, x_dir, (0, 255, 0), 2, cv2.LINE_AA)
    canvas = cv2.line(canvas, center, z_dir, (0, 0, 255), 2, cv2.LINE_AA)
    return canvas


def _rotation_mtx(rot_vec):
    a, b, g = (rot_vec * np.pi / 180.0)

    return np.array(
        [
            [np.cos(a) * np.cos(b), np.cos(a) * np.sin(b) * np.sin(g) - np.sin(a) * np.cos(g),
             np.cos(a) * np.sin(b) * np.cos(g) + np.sin(a) * np.sin(g)],
            [np.sin(a) * np.cos(b), np.sin(a) * np.sin(b) * np.sin(g) + np.cos(a) * np.cos(g),
             np.sin(a) * np.sin(b) * np.cos(g) - np.cos(a) * np.sin(g)],
            [-np.sin(b), np.cos(b) * np.sin(g), np.cos(b) * np.cos(g)]
        ]
    )


def draw_skeleton_with_background(
        canvas: np.array,
        points: List[dict],
        skip_unknown=True,
        model=COCO_MODEL_WITH_PELVIS,
        color_palette=TYPE_TO_COLOR,
        point_size=5,
        joint_width=3,
        draw_background=True,
        background_color=(195, 195, 195)
) -> np.array:
    """
    Draw skeleton to a canvas with an additional background.
    :param canvas: the target image
    :param points: points of the skeleton
    :param skip_unknown: to draw unknown skeleton points or not
    :param model: the skeleton type (for example with spine or original COCO type)
    :param color_palette: coloring of the key points and joints
    :param point_size: skeleton key point size in pixels
    :param joint_width: skeleton joint size in pixels
    :param draw_background: background drawing switch
    :param background_color: coloring behind the skeleton
    :return: image with the skeleton
    """
    back_color = {k: background_color for k in color_palette}
    if draw_background:
        canvas = _draw_skeleton(
            canvas, points,
            skip_unknown=skip_unknown,
            model=model,
            color_palette=back_color,
            point_size=point_size + 1,
            joint_width=joint_width + 3
        )
    canvas = _draw_skeleton(
        canvas, points,
        skip_unknown=skip_unknown,
        model=model,
        point_size=point_size,
        joint_width=joint_width
    )
    return canvas


def draw_nice_bounding_box(
        canvas: np.array,
        bounding_box: dict,
        color: tuple,
        scaling=1.0,
        f_border=0.0,
        shadow=True
) -> np.array:
    """
    Draw bounding box with nice dynamically changing edges and a shadow to an image.
    :param canvas: target image
    :param bounding_box: coordinates with width and height
    :param color: BGR color of the bounding box
    :param scaling: scaling factor, default for 1080p
    :param f_border: base thickness of the bounding box
    :param shadow: to visualize bounding box shadow or not
    :return: image with bounding box
    """
    if shadow:
        canvas = _draw_bounding_box(canvas, bounding_box, (0, 0, 0), scaling, 0.5)
    canvas = _draw_bounding_box(canvas, bounding_box, color, scaling, f_border)
    return canvas


def draw_nice_text(
        canvas: np.array,
        text: str,
        bounding_box: dict,
        color: tuple,
        scale=1.0,
        shadow=True
) -> np.array:
    """
    Draw text with dynamically changing size and shadow to an image top of a bounding box.
    :param canvas: target image
    :param text: drawable text
    :param bounding_box: bounding box for text location and size computation
    :param color: BRG color of the text
    :param scale: scaling factor, default for 1080p
    :param shadow: to visualize text shadow or not
    :return: image with nice text
    """
    x = bounding_box['x']
    y = bounding_box['y']
    w = bounding_box['width']

    font_size = w * scale / 60
    font_face = cv2.FONT_HERSHEY_COMPLEX_SMALL
    font_thicness = 1
    (txt_size, _) = cv2.getTextSize(text, font_face, font_size, font_thicness)

    pt1 = x * scale + w * scale / 2 - txt_size[0] / 2
    pt2 = y * scale - int(0.3 * txt_size[1])

    if shadow:
        cv2.putText(canvas, text, (int(pt1), int(pt2)), font_face, font_size, (0, 0, 0), font_thicness + 1,
                    lineType=cv2.LINE_AA)
    cv2.putText(canvas, text, (int(pt1), int(pt2)), font_face, font_size, color, font_thicness, lineType=cv2.LINE_AA)

    return canvas


def draw_overlay(
        canvas: np.array,
        overlay: np.array,
        position: Position,
        scale=None,
        margin=20
) -> np.array:
    """
    Draw images with alpha channel to the selected corner of the image.
    :param canvas: target image
    :param overlay: BGRA image
    :param position: an enum representing the corners
    :param scale: scale factor for the overlay image
    :param margin: margin around the overlay image
    :return: input image with the overlay on it
    """
    if scale:
        overlay = cv2.resize(overlay, None, fx=scale, fy=scale)

    b, g, r, alpha = cv2.split(overlay)
    overlay = cv2.merge((b, g, r))
    h, w, _ = overlay.shape
    y, x, _ = canvas.shape

    if position == Position.BOTTOM_RIGHT:
        y = y - h - margin
        x = x - w - margin
    elif position == Position.BOTTOM_LEFT:
        y = y - h - margin
        x = margin
    elif position == Position.TOP_RIGHT:
        y = margin
        x = x - w - margin
    elif position == Position.TOP_LEFT:
        y = margin
        x = margin

    roi = canvas[y:y + h, x:x + w]

    alpha = np.transpose([alpha] * 3, (1, 2, 0)) / 255.0

    alpha_roi = roi - alpha * roi
    alpha_overlay = alpha * overlay

    canvas[y:y + h, x:x + w] = cv2.add(alpha_roi, alpha_overlay)

    return canvas


def draw_head_pose(
        canvas: np.array,
        pose: dict,
        bounding_box: dict,
        scaling=1.0
) -> np.array:
    """
    Draw 3D visualized head pose on the input image.
    :param canvas: target image
    :param pose: (roll, pitch, yaw) values for the 3D lines
    :param bounding_box: bounding box for localization
    :param scaling: scaling factor, default 1080p
    :return: image with head pose
    """
    x = bounding_box['x']
    y = bounding_box['y']
    width = bounding_box['width']
    height = bounding_box['height']

    axis_length = max(width * scaling, height * scaling) / 2.5

    center = (int((x + width // 2) * scaling), int((y + height // 2) * scaling))

    pose = np.array([-pose['roll'], -pose['yaw'], -pose['pitch']])
    rotmat = _rotation_mtx(pose)

    a11 = rotmat[0, 0]
    a12 = rotmat[1, 0]
    a13 = rotmat[2, 0]
    a21 = rotmat[0, 1]
    a22 = rotmat[1, 1]
    a23 = rotmat[2, 1]

    imgpnts = [
        (int(a11 * axis_length), int(-a21 * axis_length)),
        (int(a12 * axis_length), int(-a22 * axis_length)),
        (int(a13 * axis_length), int(-a23 * axis_length))
    ]
    return _draw_3d_lines(canvas, center, imgpnts)
