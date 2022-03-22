"""
求k值，线条与摄像头距离，中心点相对摄像头角度，串口发出
NowLoadY
"""
import cv2
import numpy as np
import math
import serial
from module import settings, tools, variables


variables._init()


if settings.adjust_bar:
    def empty(a):
        h_min = cv2.getTrackbarPos("Hue Min", "TrackBars")
        h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
        s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
        s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
        v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
        v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
        canny_lth = cv2.getTrackbarPos("canny_lth", "TrackBars")
        canny_hth = cv2.getTrackbarPos("canny_hth", "TrackBars")
        return h_min, h_max, s_min, s_max, v_min, v_max, canny_lth, canny_hth


    cv2.namedWindow("TrackBars")
    cv2.resizeWindow("TrackBars", 640, 400)
    cv2.createTrackbar("Hue Min", "TrackBars", 0, 179, empty)
    cv2.createTrackbar("Hue Max", "TrackBars", 179, 179, empty)
    cv2.createTrackbar("Sat Min", "TrackBars", 0, 255, empty)
    cv2.createTrackbar("Sat Max", "TrackBars", 61, 255, empty)
    cv2.createTrackbar("Val Min", "TrackBars", 0, 255, empty)
    cv2.createTrackbar("Val Max", "TrackBars", 255, 255, empty)
    cv2.createTrackbar("canny_lth", "TrackBars", 40, 400, empty)
    cv2.createTrackbar("canny_hth", "TrackBars", 50, 400, empty)
else:
    tools.init_color_select()
    h_min = variables.get_val("h_min")
    h_max = variables.get_val("h_max")
    s_min = variables.get_val("s_min")
    s_max = variables.get_val("s_max")
    v_min = variables.get_val("v_min")
    v_max = variables.get_val("v_max")
    canny_lth = variables.get_val("canny_lth")
    canny_hth = variables.get_val("canny_hth")

cap = cv2.VideoCapture(settings.camera_path)
cap.set(3, 1280 * settings.cam_resize)
cap.set(4, 720 * settings.cam_resize)
variables.set_val("cap_width", 1280 * settings.cam_resize)
variables.set_val("cap_height", 720 * settings.cam_resize)
try:

    mcuSer = serial.Serial(settings.uart_to_car, settings.uart_to_car_baud, timeout=0.5)
    print(settings.uart_to_car + " opened successfully")
except:
    print(settings.uart_to_car + " went wrong")


def send_message_to_COM(Message):
    try:
        mcuSer.write(Message.encode('utf-8'))
        mcuSer.write(b'\n')
        print(type(Message))
        print(Message)
    except:
        print("sent |" + Message + "| but " + settings.uart_to_car + " went wrong!")


if settings.k_filt:
    ks = [0]*30
    print(ks)
    print("len of ks:"+str(len(ks)))
if settings.k_m:
    ks = []
if settings.calculate_distance:
    midws = []
chosen_y = settings.roi_shape[0]//2
while True:
    selectedContours = []
    ret, img = cap.read()
    full_img = img.copy()
    roi = [[settings.roi_x1, settings.roi_x2], [settings.roi_y1, settings.roi_y2]]
    img = img[roi[1][0]:roi[1][1], roi[0][0]:roi[0][1]]
    cv2.rectangle(full_img, (roi[0][0], roi[1][0]), (roi[0][1], roi[1][1]), (0, 255, 127), 2)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if settings.adjust_bar:
        h_min, h_max, s_min, s_max, v_min, v_max, canny_lth, canny_hth = empty(0)  # minThreshold, maxThreshold= empty(0)
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHSV, lower, upper)
    imgColorSelectResult = tools.process_img(img, mask)
    gray = cv2.cvtColor(imgColorSelectResult, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, canny_lth, canny_hth, L2gradient = True)
    lines = cv2.HoughLinesP(edges, settings.hf_rho, settings.hf_theta, settings.hf_threshold,
                            minLineLength=settings.hf_min_line_len, maxLineGap=settings.hf_max_line_gap)
    last_y = last_len = 0
    selected = False
    tools.draw_yRange(imgColorSelectResult, chosen_y)
    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x2 != x1:
                    k = (y2 - y1) / (x2 - x1)
                else:
                    k = 0.0
                if abs(k) < settings.k_max:
                    if abs(chosen_y - (y2 + y1) // 2) > settings.y_changeMax:
                        cv2.line(imgColorSelectResult, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        k = tools.process_k_to_angle(k, 3)
                        if settings.show_img:
                            cv2.putText(imgColorSelectResult, "lost! " + str(k), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (0, 0, 255), 2)
                            tools.show_imges(edges, imgColorSelectResult, full_img)
                        continue
                    if (y2 + y1) / 2 >= last_y:
                        if tools.length_calculate(x1, y1, x2, y2) >= last_len:
                            last_y = (y2 + y1) / 2
                            last_len = tools.length_calculate(x1, y1, x2, y2)
                            selected_line = line
                            selected = True

        if selected:
            x1, y1, x2, y2 = selected_line[0]
            if x2 != x1:
                k = round(-(y2 - y1) / (x2 - x1), 5)
            else:
                k = 0.000

            chosen_y = (y2 + y1) // 2
            if settings.calculate_distance:
                middle_w = round((x2 + x1) / 2, 1)
            if settings.k_m:
                ks.append(k)
            if settings.k_filt:
                for i in range(0, len(ks)):
                    if i < len(ks) - 1:
                        ks[i] = ks[i + 1]
                    else:
                        ks[i] = k
            if settings.calculate_distance:
                midws.append(middle_w)

            if len(ks) >= settings.average_nums:
                if settings.k_m:
                    k = tools.process_k_to_angle(tools.calculate_mean(ks), 3)
                    ks = []
                if settings.k_filt:
                    k = round(math.degrees(math.atan(tools.data_filter(np.array(ks)))), 3)
                if settings.calculate_distance:
                    midwm = round(tools.calculate_mean(midws), 1)
                    midws = []
                try:
                    mcuSer.write('k'.encode('utf-8'))
                    send_message_to_COM(str(k))
                except:
                    pass
                if settings.calculate_distance:
                    distance_and_angle = tools.distance_and_angle_calculate(tools.length_calculate(x1, y1, x2, y2), midwm)
            if settings.show_img:
                cv2.line(imgColorSelectResult, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(imgColorSelectResult, "angle:" + str(k), (50, settings.roi_shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
    except:
        print("no line")
    if settings.show_img:
        tools.show_imges(edges, imgColorSelectResult, full_img)
