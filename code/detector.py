"""
求k平均值，线条与摄像头距离，中心点相对摄像头角度，串口发出
NowLoadY
"""
import cv2
import numpy as np
import settings
import serial
import tools
import variables


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
        return h_min, h_max, s_min, s_max, v_min, v_max, canny_lth, canny_hth  # , minThreshold, maxThreshold


    cv2.namedWindow("TrackBars")
    cv2.resizeWindow("TrackBars", 640, 400)
    cv2.createTrackbar("Hue Min", "TrackBars", 0, 179, empty)
    cv2.createTrackbar("Hue Max", "TrackBars", 179, 179, empty)
    cv2.createTrackbar("Sat Min", "TrackBars", 0, 255, empty)
    cv2.createTrackbar("Sat Max", "TrackBars", 255, 255, empty)
    cv2.createTrackbar("Val Min", "TrackBars", 0, 255, empty)
    cv2.createTrackbar("Val Max", "TrackBars", 255, 255, empty)
    cv2.createTrackbar("canny_lth", "TrackBars", 36, 400, empty)
    cv2.createTrackbar("canny_hth", "TrackBars", 67, 400, empty)
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
##############和底层通信的串口设置#############
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

ks = []
midws = []
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
    imgColorSelectResult = cv2.bitwise_and(img, img, mask=mask)
    imgColorSelectResult = cv2.GaussianBlur(imgColorSelectResult, (15, 15), 0)
    gray = cv2.cvtColor(imgColorSelectResult, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, canny_lth, canny_hth)
    lines = cv2.HoughLinesP(edges, settings.hf_rho, settings.hf_theta, settings.hf_threshold,
                            minLineLength=settings.hf_min_line_len, maxLineGap=settings.hf_max_line_gap)

    last_y = 0
    selected = False
    try:
        for i, line in enumerate(lines):
            for x1, y1, x2, y2 in line:
                if x2 == x1:
                    x2+=0.001
                k = (y2 - y1) / (x2 - x1)
                if abs(k) < settings.k_max:
                    if (y2 + y1) / 2 >= last_y:
                        last_y = (y2 + y1) / 2
                        selected_line = line
                        selected = True
        if selected:
            for x1, y1, x2, y2 in selected_line:
                if x2 == x1:
                    x2+=0.001
                k = round(-(y2 - y1) / (x2 - x1), 5)
                middle_w = round((x2 + x1) / 2, 1)
                ks.append(k)
                midws.append(middle_w)
                cv2.line(imgColorSelectResult, (x1, y1), (x2, y2), (0, 255, 0), 1)
            if len(ks) >= settings.average_nums:
                km = round(tools.calculate_mean(ks), 2)
                midwm = round(tools.calculate_mean(midws), 1)
                ks = []
                midws = []
                try:
                    mcuSer.write('k'.encode('utf-8'))
                    send_message_to_COM(str(km))

                    mcuSer.write('j'.encode('utf-8'))
                    send_message_to_COM(str(midwm))
                except:
                    pass
                distance_and_angle = tools.distance_and_angle_calculate(tools.length_calculate(x1, y1, x2, y2), midwm)
            if settings.show_img:
                cv2.putText(imgColorSelectResult, "distance:" + str(distance_and_angle[0]), (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0),
                            2)
                cv2.putText(imgColorSelectResult, "angle:" + str(distance_and_angle[1]), (50, 110), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0),
                            2)
                cv2.putText(imgColorSelectResult, "k:" + str(km), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
    except:
        pass
    if settings.show_img:
        cv2.line(imgColorSelectResult, (settings.roi_shape[1]//2, 0), (settings.roi_shape[1]//2, settings.roi_shape[0]), (0, 200, 200), 1)
        cv2.imshow('edges', edges)
        cv2.imshow('imgColorSelectResult', imgColorSelectResult)
        cv2.imshow('input', full_img)
        cv2.waitKey(1)
