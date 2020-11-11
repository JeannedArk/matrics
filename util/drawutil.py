# -*- coding: utf-8 -*-
import cv2

# Colors
COLOR_BLUE = (255, 0, 0)
COLOR_RED = (0, 0, 255)

# Rectangle
THICKNESS = 5

# Text
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 2
LINE_TYPE = 6
TEXT_PADDING_X = 15
TEXT_PADDING_Y = 40


def draw_ATDs_on_img(img_path, atd_records):
    cv_img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    for atd_record in atd_records:
        if atd_record.widget_o is not None:
            v_bounds = atd_record.widget_o.visible_boundaries
            x1 = v_bounds.leftX
            y1 = v_bounds.topY
            x2 = x1 + v_bounds.width
            y2 = y1 + v_bounds.height
            # Draw the rectangle box for marking the widget
            cv2.rectangle(cv_img, (x1, y1), (x2, y2), COLOR_BLUE, THICKNESS)
            # Draw the id
            cv2.putText(cv_img,
                        str(atd_record.id),
                        (x1 + TEXT_PADDING_X, y1 + TEXT_PADDING_Y),
                        FONT,
                        FONT_SCALE,
                        COLOR_RED,
                        LINE_TYPE)
    return cv_img


def resize_img(img_path, scale_factor):
    oriimg = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    # This can happen if there are faulty images
    if oriimg is None:
        raise IOError(f"Could not load image: {img_path}")
    newX, newY = oriimg.shape[1] * scale_factor, oriimg.shape[0] * scale_factor
    return cv2.resize(oriimg, (int(newX), int(newY)), interpolation=cv2.INTER_AREA)


def dump_cv_img(img, new_img_path):
    write = cv2.imwrite(new_img_path, img)
    assert write, f"Dumping cv image was not successful: {new_img_path}"
