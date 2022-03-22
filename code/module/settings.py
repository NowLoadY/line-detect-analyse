import numpy

# 功能开关
show_img = True
adjust_bar = False
k_m = False
k_filt = True
calculate_distance = False  # 不用这个了


# 视觉设置
camera_path = 0
cam_resize = 0.5
KnownLength = 0.5  # m
cam_mtx = numpy.array([[988.47622404, 0, 647.32706248],
                       [0, 988.39096787, 370.00537205],
                       [0, 0, 1]])
cam_focal_length = (cam_mtx[0][0] + cam_mtx[1][1]) / 2*cam_resize
roi_x1 = int((1280*cam_resize * 1) // 7)
roi_x2 = int((1280*cam_resize * 6) // 7)
roi_y1 = int((720*cam_resize * 2) // 7)
roi_y2 = int((720*cam_resize * 7) // 7)
roi_shape = [int(roi_y2-roi_y1), int(roi_x2-roi_x1)]
# 直线检测设置
hf_rho = 1
hf_theta = numpy.pi / 180
hf_threshold = 70
hf_min_line_len = 350*cam_resize
hf_max_line_gap = 70*cam_resize
y_changeMax = roi_shape[0]//6

# 串口设置
uart_to_car = "COM12"
uart_to_car_baud = 115200

# k筛选条件&中心点筛选条件
k_max = 0.35
average_nums = 1
