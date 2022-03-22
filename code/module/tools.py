import math
import numpy
import cv2
from scipy.signal import savgol_filter
from module import settings, variables


def calculate_mean(list):
    add = 0
    for k in list:
        add += k
    result = add/len(list)
    return result


def init_color_select():
    variables.set_val("h_min", 0)
    variables.set_val("h_max", 179)
    variables.set_val("s_min", 0)
    variables.set_val("s_max", 255)
    variables.set_val("v_min", 0)
    variables.set_val("v_max", 255)
    variables.set_val("canny_lth", 60)
    variables.set_val("canny_hth", 80)


def length_calculate(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


def distance_and_angle_calculate(len, midw):
    return [round(settings.KnownLength/len*settings.cam_focal_length, 2),
            round(math.degrees(numpy.arctan(((settings.roi_shape[1]/2 - midw)/settings.cam_focal_length))), 1)]


def data_filter(data):
    result = savgol_filter(data, 17, 2, mode='nearest').tolist()
    return result[len(result)-2]


def show_imges(edges, imgColorSelectResult, full_img):
    cv2.line(imgColorSelectResult, (settings.roi_shape[1] // 2, 0),
             (settings.roi_shape[1] // 2, settings.roi_shape[0]), (0, 200, 200), 1)
    cv2.imshow('edges', edges)
    cv2.imshow('imgColorSelectResult', imgColorSelectResult)
    cv2.imshow('input', full_img)
    cv2.waitKey(1)


def process_k_to_angle(k, afterPoint):
    return round(math.degrees(math.atan(k)), afterPoint)


def process_img(img, mask):
    imgColorSelectResult = cv2.bitwise_and(img, img, mask=mask)
    imgColorSelectResult = cv2.GaussianBlur(imgColorSelectResult, (9, 9), 0)
    return cv2.bilateralFilter(imgColorSelectResult, 25, 60, 255)


def draw_yRange(imgColorSelectResult, chosen_y):
    cv2.line(imgColorSelectResult, (0, chosen_y), (settings.roi_shape[1], chosen_y), (0, 100, 200), 2)
    cv2.line(imgColorSelectResult, (0, chosen_y - settings.y_changeMax),
             (settings.roi_shape[1], chosen_y - settings.y_changeMax), (0, 160, 200), 1)
    cv2.line(imgColorSelectResult, (0, chosen_y + settings.y_changeMax),
             (settings.roi_shape[1], chosen_y + settings.y_changeMax), (0, 160, 200), 1)