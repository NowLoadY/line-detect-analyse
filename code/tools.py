import settings
import variables
import numpy
import math


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
    variables.set_val("canny_lth", 30)
    variables.set_val("canny_hth", 30)


def length_calculate(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


def distance_and_angle_calculate(len, midw):
    return [round(settings.KnownLength/len*settings.cam_focal_length, 2),
            round(math.degrees(numpy.arctan(((settings.roi_shape[1]/2 - midw)/settings.cam_focal_length))), 1)]
