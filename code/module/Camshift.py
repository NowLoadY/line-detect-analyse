import cv2
from module import variables


def tracker_init(frame, x, y, w, h):
    track_roi = frame[y:y + h, x:x + w]
    hsv_roi = cv2.cvtColor(track_roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, (0, 0, 0), (255, 255, 255))
    roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    variables.set_val("track_window", (x, y, w, h))
    variables.set_val("roi_hist", roi_hist)
    variables.set_val("term_crit", term_crit)
    variables.set_val("Camshift_init", True)

def tracker(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0], variables.get_val("roi_hist"), [0, 180], 1)
    cv2.imshow("dst", dst)
    ret, track_box = cv2.CamShift(dst, variables.get_val("track_window"), variables.get_val("term_crit"))
    cv2.rectangle(frame, (track_box[0],track_box[1]), (track_box[0]+track_box[2], track_box[1]+track_box[3]), (0, 255, 0), 3)
    variables.set_val("track_window", track_box)
    return track_box
